quiz_validation = """
    You are given a quiz in LaTeX format. Your job is to analyze and refine the questions to ensure they are complete, clear, and solvable. Follow these guidelines strictly:
    - Strictly use _ for subscript and ^ for superscript in latex
    - In latex never user \\ for new line, and never use [label=*] and \\label, never use \\setcounter
    - Dont use '\setcounter' in latex
    1. Validation:
        Assess the validity and correctness of each question.
        Assess the correctness of options and the answers also, If answer is not in the options, add the correct answer and update the key
    2. Enhancement:
        If a question lacks sufficient information or requires additional details for solving, update it by adding the necessary context or clarifications.
    3. Preservation:
        If a question is already meaningful, accurate, and contains all the necessary details, leave it unchanged.
        UPDATE THE OPTIONS IF THEY ARE NOT MEANINGFUL/CORRECT
    Your goal is to produce an improved version of the provided quiz with all 10 questions where all questions are clear, appropriate, and solvable with correct options and answers.
    Quiz is {content}
"""
