from taipy.gui import builder as tgb
from taipy.gui import navigate


def go_to_data(state):
    navigate(state, to="data", force=True)


with tgb.Page() as home_page:
    tgb.text("Welcome to JobUnify - Your Ultimate Job Search Platform", class_name="h1")
    tgb.html("br")
    tgb.text(
        "Begin your journey to career success with JobUnify. Our platform aggregates job listings from top websites, ensuring you have access to the widest range of opportunities in one convenient location."
    )
    tgb.html("br")
    tgb.text("Explore Diverse Opportunities", class_name="h3")
    tgb.text(
        "Browse through thousands of job listings across various industries, from software development to marketing, finance, healthcare, and more. Whatever your expertise or career aspirations, JobUnify has something for you."
    )
    tgb.html("br")
    tgb.text("Smart Search and Filtering", class_name="h3")
    tgb.text(
        "Use our advanced search and filtering tools to narrow down your options based on location, salary, job type, and more. Spend less time searching and more time applying to the perfect positions."
    )
    tgb.html("br")
    tgb.text("Stay Updated and Informed", class_name="h3")
    tgb.text(
        "Receive real-time updates on new job postings, industry trends, and career advice. Our platform keeps you informed every step of the way, ensuring you never miss out on important opportunities."
    )
    tgb.button(label="Get started", on_action=go_to_data)
