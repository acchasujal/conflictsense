import json
import random

# Seed for deterministic generation
random.seed(42)

first_names_in = ["Aarav", "Arjun", "Vihaan", "Aditya", "Sai", "Krishna", "Ishaan", "Shaurya", "Atharva", "Pranav", 
                  "Ananya", "Diya", "Ira", "Aadhya", "Saanvi", "Myra", "Aanya", "Pari", "Anika", "Riya", "Kavya", 
                  "Rohan", "Dev", "Rahul", "Amit", "Siddharth", "Preeti", "Neha", "Priya", "Anjali", "Suresh", "Ramesh"]
last_names_in = ["Sharma", "Patel", "Verma", "Gupta", "Kumar", "Singh", "Mehta", "Joshi", "Rao", "Nair", "Iyer", 
                 "Mukherjee", "Chatterjee", "Reddy", "Choudhury", "Bose", "Das", "Sen", "Pillai", "Mishra", "Trivedi"]

first_names_global = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Emily", "Frank", "Grace", "Henry", 
                      "Ivy", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia", "Peter", "Quinn", "Rachel", 
                      "Sam", "Thomas", "Ursula", "Victor", "Wendy", "Xavier", "Yvonne", "Zachary", "Sarah", "Michael"]
last_names_global = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                     "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

departments = ["Engineering", "HR", "Finance", "Legal", "Sales", "Marketing", "Operations", "Product"]
roles = {
    "Engineering": ["Software Engineer", "QA Engineer", "DevOps Engineer", "Engineering Manager", "Solutions Architect"],
    "HR": ["HR Specialist", "Recruiter", "HR Manager", "HR Generalist"],
    "Finance": ["Accountant", "Finance Analyst", "Finance Manager", "Billing Specialist"],
    "Legal": ["Legal Counsel", "Compliance Officer", "Legal Assistant"],
    "Sales": ["Account Executive", "Sales Representative", "Sales Manager"],
    "Marketing": ["Marketing Specialist", "Content Writer", "SEO Analyst"],
    "Operations": ["Operations Associate", "Operations Manager", "Support Specialist"],
    "Product": ["Product Manager", "UX Designer", "Product Owner"]
}

employees = []

# Generate 34 India-resident remote employees
for i in range(1, 35):
    fname = random.choice(first_names_in)
    lname = random.choice(last_names_in)
    dept = random.choice(["Engineering", "Product", "Operations"])
    role = random.choice(roles[dept])
    employees.append({
        "id": f"EMP-IN-{i:03d}",
        "name": f"{fname} {lname}",
        "location": "India",
        "department": dept,
        "role": role,
        "is_remote": True,
        "compensation_situation": "standard",
        "qualifies_compensation_exception": False
    })

# Generate 12 employees in qualifying compensation situations
# Compensation entitlement: automatic vs. discretionary (Handbook §8.3 vs Finance §5.1)
# Relocated to regional offices, expecting standard relocation allowance of $5000.
for i in range(1, 13):
    fname = random.choice(first_names_global)
    lname = random.choice(last_names_global)
    dept = random.choice(["Engineering", "Sales", "Operations", "Marketing"])
    role = random.choice(roles[dept])
    # Let's place them in regional offices (e.g. Chicago, London, Singapore, Sydney)
    loc = random.choice(["United States (Chicago Office)", "United Kingdom (London Office)", "Singapore", "Australia (Sydney Office)"])
    employees.append({
        "id": f"EMP-COMP-{i:03d}",
        "name": f"{fname} {lname}",
        "location": loc,
        "department": dept,
        "role": role,
        "is_remote": False,
        "compensation_situation": "relocation_pending_allowance",
        "qualifies_compensation_exception": True
    })

# Generate the remaining 1154 employees to make up exactly 1200 employees
total_headcount = 1200
current_count = len(employees)
remaining_count = total_headcount - current_count

for i in range(1, remaining_count + 1):
    # Mostly global, some Indian
    is_in = random.random() < 0.1
    if is_in:
        fname = random.choice(first_names_in)
        lname = random.choice(last_names_in)
        loc = "India"
        is_remote = random.random() < 0.5  # not part of the remote 34 if not marked remote or if they are in office
    else:
        fname = random.choice(first_names_global)
        lname = random.choice(last_names_global)
        loc = random.choice(["United States (HQ)", "United Kingdom", "Canada", "Germany", "Japan"])
        is_remote = random.random() < 0.3

    dept = random.choice(departments)
    role = random.choice(roles[dept])
    
    # Ensure they don't overlap with the remote 34 or compensation 12 classifications
    # (if they are in India, they are in office to avoid inflating the 34 remote count)
    if loc == "India":
        is_remote = False
        
    employees.append({
        "id": f"EMP-GEN-{i:04d}",
        "name": f"{fname} {lname}",
        "location": loc,
        "department": dept,
        "role": role,
        "is_remote": is_remote,
        "compensation_situation": "standard",
        "qualifies_compensation_exception": False
    })

# Shuffle the employees for a realistic list, keeping IDs traceable
random.shuffle(employees)

with open("mock_data/employees.json", "w", encoding="utf-8") as f:
    json.dump(employees, f, indent=2, ensure_ascii=False)

print(f"Successfully generated mock_data/employees.json with {len(employees)} employees.")
print(f"India-resident remote employees: {len([e for e in employees if e['location'] == 'India' and e['is_remote']])}")
print(f"Compensation exception employees: {len([e for e in employees if e['qualifies_compensation_exception']])}")
