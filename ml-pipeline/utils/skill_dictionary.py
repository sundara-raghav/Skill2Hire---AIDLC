"""
Skill Dictionary Module

Provides skill taxonomy and categorization for the placement prediction system.
"""

# Skill categories and taxonomy
SKILL_CATEGORIES = {
    'technical': [
        'Python', 'Java', 'C++', 'JavaScript', 'SQL', 'HTML', 'CSS',
        'React', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring Boot',
        'Machine Learning', 'Data Science', 'Deep Learning', 'NLP',
        'Data Structures', 'Algorithms', 'System Design', 'OOP',
        'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
        'MongoDB', 'PostgreSQL', 'MySQL', 'Redis',
        'REST API', 'GraphQL', 'Microservices'
    ],
    'soft': [
        'Communication', 'Teamwork', 'Leadership', 'Problem Solving',
        'Critical Thinking', 'Time Management', 'Adaptability',
        'Creativity', 'Collaboration', 'Presentation Skills'
    ],
    'domain': [
        'Web Development', 'Mobile Development', 'Cloud Computing',
        'DevOps', 'Data Engineering', 'Business Intelligence',
        'Cybersecurity', 'Blockchain', 'IoT', 'AR/VR'
    ]
}

# Skill importance weights (for skill gap analysis)
SKILL_WEIGHTS = {
    'Python': 0.9,
    'Java': 0.9,
    'SQL': 0.8,
    'Data Structures': 0.9,
    'Algorithms': 0.9,
    'Machine Learning': 0.7,
    'Communication': 0.8,
    'Problem Solving': 0.9,
    'Teamwork': 0.7
}


def get_all_skills():
    """Get all skills from all categories."""
    all_skills = []
    for category_skills in SKILL_CATEGORIES.values():
        all_skills.extend(category_skills)
    return all_skills


def get_skills_by_category(category):
    """
    Get skills for a specific category.
    
    Args:
        category (str): Category name ('technical', 'soft', 'domain')
    
    Returns:
        list: List of skills in the category
    """
    return SKILL_CATEGORIES.get(category, [])


def get_skill_weight(skill):
    """
    Get importance weight for a skill.
    
    Args:
        skill (str): Skill name
    
    Returns:
        float: Weight (0.0-1.0), default 0.5 if not found
    """
    return SKILL_WEIGHTS.get(skill, 0.5)


def categorize_skill(skill):
    """
    Determine category for a given skill.
    
    Args:
        skill (str): Skill name
    
    Returns:
        str: Category name or 'unknown'
    """
    for category, skills in SKILL_CATEGORIES.items():
        if skill in skills:
            return category
    return 'unknown'
