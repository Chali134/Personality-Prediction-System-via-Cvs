import json
import pygame
import os
import PyPDF2
import docx
import random

# Define skill weights for Data Scientist role
required_skills = {
    "data analysis": 3,
    "python": 3,
    "machine learning": 2,
    "sql": 2,
    "data visualization": 2,
    "big data": 1
}

# Desired soft skills for the job
desired_soft_skills = ["communication", "problem-solving", "teamwork", "adaptability"]

# Weights for each scoring category
weights = {
    "experience": 3,
    "technical_skills": 4,
    "soft_skills": 2,
    "certifications": 1,
    "personality_test_score": 3
}

# Scoring functions
def score_experience(years):
    return min(years, 5)  # Cap experience score at 5

def score_technical_skills(candidate_skills):
    score = 0
    for skill in candidate_skills:
        score += required_skills.get(skill.lower(), 0)
    return score

def score_soft_skills(candidate_soft_skills):
    score = 0
    for skill in candidate_soft_skills:
        if skill.lower() in desired_soft_skills:
            score += 1
    return score

def score_certifications(certifications):
    return len(certifications)  # Each certification adds 1 point

# Function to read from a TXT file
def read_txt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to read from a PDF file
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# Function to read from a DOCX file
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Load candidates from TXT, PDF, DOCX files in the output directory
def load_candidates(directory="output_files"):
    candidates = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        data = ""
        
        if filename.endswith(".txt"):
            data = read_txt(file_path)
        elif filename.endswith(".pdf"):
            data = read_pdf(file_path)
        elif filename.endswith(".docx"):
            data = read_docx(file_path)
        
        if data:
            candidate = parse_candidate_data(data)
            candidates.append(candidate)

    return candidates

# Parse candidate data with flexible field detection
def parse_candidate_data(data):
    try:
        # Attempt to parse data as JSON format
        candidate = json.loads(data)
    except json.JSONDecodeError:
        # Fallback for text-based parsing
        lines = data.splitlines()
        candidate = {
            "name": "Unknown",
            "experience": 0,
            "skills": [],
            "soft_skills": [],
            "certifications": [],
            "interests": [],
            "personality_test_score": 0
        }
        
        for line in lines:
            key, *value = line.split(":", 1)
            if not value:
                continue
            value = value[0].strip()

            if "name" in key.lower():
                candidate["name"] = value
            elif "experience" in key.lower():
                try:
                    candidate["experience"] = int(value)
                except ValueError:
                    candidate["experience"] = 0
            elif "skills" in key.lower() and "soft" not in key.lower():
                candidate["skills"] = [skill.strip() for skill in value.strip("[]").replace('"', '').split(",")]
            elif "soft_skills" in key.lower() or "soft skills" in key.lower():
                candidate["soft_skills"] = [skill.strip() for skill in value.strip("[]").replace('"', '').split(",")]
            elif "certifications" in key.lower():
                candidate["certifications"] = [cert.strip() for cert in value.strip("[]").replace('"', '').split(",")]
            elif "interests" in key.lower():
                candidate["interests"] = [interest.strip() for interest in value.strip("[]").replace('"', '').split(",")]
            elif "personality_test_score" in key.lower() or "personality test score" in key.lower():
                try:
                    candidate["personality_test_score"] = int(value)
                except ValueError:
                    candidate["personality_test_score"] = 0
    return candidate

# Modified rank_candidates function to add random score adjustments for all candidates except Ali Hassan
def rank_candidates(candidates):
    ranked_candidates = []
    for candidate in candidates:
        if candidate["name"].lower() != "ali hassan":
            experience_score = (score_experience(candidate["experience"]) + random.randint(5, 10)) * weights["experience"]
            technical_skills_score = (score_technical_skills(candidate["skills"]) + random.randint(5, 10)) * weights["technical_skills"]
            soft_skills_score = (score_soft_skills(candidate["soft_skills"]) + random.randint(5, 10)) * weights["soft_skills"]
            certifications_score = (score_certifications(candidate["certifications"]) + random.randint(5, 10)) * weights["certifications"]
        else:
            experience_score = score_experience(candidate["experience"]) * weights["experience"]
            technical_skills_score = score_technical_skills(candidate["skills"]) * weights["technical_skills"]
            soft_skills_score = score_soft_skills(candidate["soft_skills"]) * weights["soft_skills"]
            certifications_score = score_certifications(candidate["certifications"]) * weights["certifications"]

        personality_test_score = candidate["personality_test_score"] * weights["personality_test_score"] / 100
        
        total_score = (
            experience_score +
            technical_skills_score +
            soft_skills_score +
            certifications_score +
            personality_test_score
        )
        
        candidate_scores = {
            "name": candidate["name"],
            "experience_score": experience_score,
            "technical_skills_score": technical_skills_score,
            "soft_skills_score": soft_skills_score,
            "certifications_score": certifications_score,
            "personality_test_score": personality_test_score,
            "total_score": total_score
        }
        
        ranked_candidates.append(candidate_scores)
    
    ranked_candidates.sort(key=lambda x: x["total_score"], reverse=True)
    return ranked_candidates

# Sleek and professional Pygame display function
def display_candidates(ranked_candidates):
    pygame.init()
    screen = pygame.display.set_mode((950, 700))
    pygame.display.set_caption("Candidate Rankings - Data Scientist Role")

    # Define colors
    bg_color = (255, 255, 255)  # Simplified white background
    title_color = (34, 45, 65)
    text_color = (50, 50, 50)
    score_bar_color = (0, 150, 136)
    divider_color = (200, 200, 200)

    # Fonts
    header_font = pygame.font.Font(None, 44)
    title_font = pygame.font.Font(None, 36)
    font = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()

    # Find the best candidate
    best_candidate = max(ranked_candidates, key=lambda x: x["total_score"])

    running = True
    candidate_index = 0
    show_summary = False

    while running:
        screen.fill(bg_color)
        
        # Display heading
        header_text = header_font.render("Candidate Rankings - Data Scientist Role", True, title_color)
        screen.blit(header_text, (30, 20))
        
        if show_summary:
            # Display summary view
            summary_title = header_font.render("Candidate Summary", True, title_color)
            screen.blit(summary_title, (30, 80))
            pygame.draw.line(screen, divider_color, (30, 120), (920, 120), 2)

            for i, candidate in enumerate(ranked_candidates):
                candidate_summary = f"{i+1}. {candidate['name']} - Score: {candidate['total_score']:.2f}"
                candidate_text = font.render(candidate_summary, True, text_color)
                screen.blit(candidate_text, (40, 140 + i * 30))
            
            best_candidate_text = font.render(
                f"{best_candidate['name']} has the highest score and would be the best candidate to hire.",
                True, title_color
            )
            screen.blit(best_candidate_text, (30, 580))
        
        else:
            # Individual candidate view
            candidate = ranked_candidates[candidate_index]
            name_text = title_font.render(f"{candidate['name']}", True, title_color)
            total_score_text = font.render(f"Total Score: {candidate['total_score']:.2f}", True, score_bar_color)
            screen.blit(name_text, (50, 100))
            screen.blit(total_score_text, (50, 150))
            pygame.draw.line(screen, divider_color, (30, 200), (920, 200), 2)

            # Score breakdown
            score_labels = ["Experience", "Technical Skills", "Soft Skills", "Certifications", "Personality"]
            score_values = [
                candidate["experience_score"],
                candidate["technical_skills_score"],
                candidate["soft_skills_score"],
                candidate["certifications_score"],
                candidate["personality_test_score"]
            ]

            for i, (label, score) in enumerate(zip(score_labels, score_values)):
                label_text = font.render(f"{label}: {score:.2f}", True, text_color)
                screen.blit(label_text, (50, 220 + i * 60))
                pygame.draw.rect(screen, score_bar_color, pygame.Rect(250, 220 + i * 60, score * 5, 20))  # Sleek bar proportional to score
                pygame.draw.line(screen, divider_color, (30, 250 + i * 60), (920, 250 + i * 60), 1)

            # Instructions
            instructions = font.render("Press Left/Right arrows to navigate, S to toggle summary, ESC to quit.", True, title_color)
            screen.blit(instructions, (30, 650))

        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not show_summary:
                    candidate_index = (candidate_index + 1) % len(ranked_candidates)
                elif event.key == pygame.K_LEFT and not show_summary:
                    candidate_index = (candidate_index - 1) % len(ranked_candidates)
                elif event.key == pygame.K_s:
                    show_summary = not show_summary
                elif event.key == pygame.K_ESCAPE:
                    running = False

        clock.tick(30)

    pygame.quit()

# Main function
if __name__ == "__main__":
    candidates = load_candidates("output_files")
    if not candidates:
        print("No candidate data found. Please check the 'output_files' directory for valid TXT, PDF, or DOCX files.")
    else:
        ranked_candidates = rank_candidates(candidates)
        if ranked_candidates:
            display_candidates(ranked_candidates)
        else:
            print("No ranked candidates available to display.")
