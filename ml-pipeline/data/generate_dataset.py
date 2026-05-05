"""
Dataset Generation Module

Generates synthetic student dataset with realistic distributions and correlations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.validation import validate_dataset, validate_student_profile
from utils.logger import setup_logger

logger = setup_logger()


def generate_student_profile(seed=None) -> Dict:
    """
    Generate a single student profile with realistic correlations.
    
    Args:
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        dict: Student profile data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate base features
    cgpa = np.clip(np.random.normal(Config.CGPA_MEAN, Config.CGPA_STD), 0.0, 10.0)
    aptitude_score = np.clip(np.random.normal(Config.APTITUDE_MEAN, Config.APTITUDE_STD), 0, 100)
    
    # Programming skills (moderate correlation with CGPA)
    base_prog_skills = np.random.randint(1, 11)
    if cgpa > 8.0:
        programming_skills = min(base_prog_skills + 1, 10)
    elif cgpa < 5.0:
        programming_skills = max(base_prog_skills - 1, 1)
    else:
        programming_skills = base_prog_skills
    
    # Communication skills (weak correlation with CGPA)
    base_comm_skills = np.random.randint(1, 11)
    if cgpa > 8.5 and np.random.random() < 0.2:
        communication_skills = min(base_comm_skills + 1, 10)
    else:
        communication_skills = base_comm_skills
    
    # Number of projects (moderate correlation with programming skills)
    base_projects = np.random.poisson(Config.PROJECTS_LAMBDA)
    if programming_skills >= 8:
        num_projects = min(base_projects + 1, 10)
    else:
        num_projects = min(base_projects, 10)
    
    # Internship experience (moderate correlation with CGPA and projects)
    prob = Config.INTERNSHIP_BASE_PROB
    if cgpa > 7.5:
        prob += 0.2
    if num_projects >= 3:
        prob += 0.1
    prob = min(prob, 1.0)
    internship_experience = 1 if np.random.random() < prob else 0
    
    # Certifications count (moderate correlation with programming skills)
    base_certs = np.random.poisson(Config.CERTIFICATIONS_LAMBDA)
    if programming_skills >= 7:
        certifications_count = min(base_certs + 1, 10)
    else:
        certifications_count = min(base_certs, 10)
    
    # Branch (realistic distribution)
    branches = list(Config.BRANCH_DISTRIBUTION.keys())
    probabilities = list(Config.BRANCH_DISTRIBUTION.values())
    branch = np.random.choice(branches, p=probabilities)
    
    # Calculate placement probability using weighted formula
    placement_score = (
        cgpa * Config.PLACEMENT_WEIGHTS['cgpa'] +
        (aptitude_score / 100) * Config.PLACEMENT_WEIGHTS['aptitude'] +
        (programming_skills / 10) * Config.PLACEMENT_WEIGHTS['programming'] +
        (communication_skills / 10) * Config.PLACEMENT_WEIGHTS['communication'] +
        (num_projects / 10) * Config.PLACEMENT_WEIGHTS['projects'] +
        internship_experience * Config.PLACEMENT_WEIGHTS['internship'] +
        (certifications_count / 10) * Config.PLACEMENT_WEIGHTS['certifications']
    )
    
    # Normalize to [0, 1]
    placement_probability = placement_score / 10.0
    
    # Determine placement status (will be adjusted for balance)
    placement_status = 1 if placement_probability >= 0.5 else 0
    
    profile = {
        'cgpa': round(cgpa, 2),
        'aptitude_score': int(aptitude_score),
        'programming_skills': int(programming_skills),
        'communication_skills': int(communication_skills),
        'num_projects': int(num_projects),
        'internship_experience': int(internship_experience),
        'certifications_count': int(certifications_count),
        'branch': branch,
        'placement_status': int(placement_status),
        'placement_probability': round(placement_probability, 4)
    }
    
    return profile


def is_duplicate(profile: Dict, existing_profiles: List[Dict]) -> bool:
    """
    Check if profile is duplicate of any existing profile.
    
    Args:
        profile (dict): Profile to check
        existing_profiles (list): List of existing profiles
    
    Returns:
        bool: True if duplicate found
    """
    for existing in existing_profiles:
        if all([
            profile['cgpa'] == existing['cgpa'],
            profile['aptitude_score'] == existing['aptitude_score'],
            profile['programming_skills'] == existing['programming_skills'],
            profile['communication_skills'] == existing['communication_skills'],
            profile['num_projects'] == existing['num_projects'],
            profile['internship_experience'] == existing['internship_experience'],
            profile['certifications_count'] == existing['certifications_count'],
            profile['branch'] == existing['branch']
        ]):
            return True
    return False


def balance_dataset(profiles: List[Dict]) -> List[Dict]:
    """
    Adjust placement status to achieve 50/50 class balance.
    
    Args:
        profiles (list): List of student profiles
    
    Returns:
        list: Balanced profiles
    """
    # Sort by placement probability
    sorted_profiles = sorted(profiles, key=lambda x: x['placement_probability'])
    
    # Calculate target counts
    total = len(sorted_profiles)
    target_placed = total // 2
    
    # Assign placement status based on probability ranking
    for i, profile in enumerate(sorted_profiles):
        if i < total - target_placed:
            profile['placement_status'] = 0
        else:
            profile['placement_status'] = 1
    
    return sorted_profiles


def generate_synthetic_dataset(target_size=1000, seed=42) -> pd.DataFrame:
    """
    Generate complete synthetic dataset with balanced classes.
    
    Args:
        target_size (int): Target number of records
        seed (int): Random seed for reproducibility
    
    Returns:
        pd.DataFrame: Generated dataset
    """
    logger.info(f"Generating synthetic dataset (target: {target_size} records, seed: {seed})")
    
    # Set global seed
    np.random.seed(seed)
    
    profiles = []
    attempts = 0
    max_attempts = target_size * 10  # Prevent infinite loop
    
    while len(profiles) < target_size and attempts < max_attempts:
        # Generate profile with incremented seed for variety
        profile = generate_student_profile(seed=seed + attempts)
        
        # Validate profile
        is_valid, errors = validate_student_profile(profile)
        if not is_valid:
            logger.warning(f"Invalid profile generated: {errors}")
            attempts += 1
            continue
        
        # Check for duplicates
        if is_duplicate(profile, profiles):
            attempts += 1
            continue
        
        profiles.append(profile)
        attempts += 1
        
        # Log progress
        if len(profiles) % 100 == 0:
            logger.info(f"Generated {len(profiles)}/{target_size} records")
    
    if len(profiles) < target_size:
        logger.warning(f"Only generated {len(profiles)}/{target_size} records after {max_attempts} attempts")
    
    # Balance dataset
    logger.info("Balancing dataset (50% placed, 50% not placed)")
    profiles = balance_dataset(profiles)
    
    # Convert to DataFrame
    df = pd.DataFrame(profiles)
    
    # Log statistics
    placed_count = df['placement_status'].sum()
    placed_ratio = placed_count / len(df)
    logger.info(f"Dataset generated: {len(df)} records ({placed_count} placed, {len(df) - placed_count} not placed)")
    logger.info(f"Class balance: {placed_ratio:.2%} placed")
    
    return df


def generate_dataset_with_retry(target_size=1000, max_retries=3, base_seed=42) -> pd.DataFrame:
    """
    Generate dataset with retry mechanism (different seed on each attempt).
    
    Args:
        target_size (int): Target number of records
        max_retries (int): Maximum number of retry attempts
        base_seed (int): Base random seed
    
    Returns:
        pd.DataFrame: Generated dataset
    
    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            seed = base_seed + attempt
            logger.info(f"Dataset generation attempt {attempt + 1}/{max_retries} (seed: {seed})")
            
            dataset = generate_synthetic_dataset(target_size, seed=seed)
            
            # Validate dataset
            is_valid, errors = validate_dataset(dataset)
            if not is_valid:
                logger.warning(f"Dataset validation failed: {errors}")
                if attempt < max_retries - 1:
                    logger.info("Retrying with different seed...")
                    continue
                else:
                    raise Exception(f"Dataset validation failed after {max_retries} attempts: {errors}")
            
            logger.info(f"Dataset generation successful on attempt {attempt + 1}")
            return dataset
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise Exception(f"Dataset generation failed after {max_retries} attempts: {e}")
    
    raise Exception("Dataset generation failed (unexpected error)")


if __name__ == '__main__':
    # Test dataset generation
    df = generate_dataset_with_retry(target_size=100, max_retries=3, base_seed=42)
    print(f"\nGenerated dataset shape: {df.shape}")
    print(f"\nFirst 5 records:\n{df.head()}")
    print(f"\nDataset statistics:\n{df.describe()}")
