"""
F11: Legal Precedent & Case Similarity Engine
Seed historical cases database with 50 diverse legal precedents
"""
from app import create_app, db
from app.models import HistoricalCase
from datetime import datetime, timedelta
import random

app = create_app()

# 50 diverse historical legal cases covering various types
HISTORICAL_CASES = [
    # CRIMINAL CASES (15)
    {
        "case_number": "CRL/2020/001",
        "case_type": "Criminal",
        "title": "State vs. Rajesh Kumar - Murder under Section 302 IPC",
        "description": "The accused was charged with murder under Section 302 IPC after a dispute over property. The victim was found dead with multiple stab wounds. The prosecution presented forensic evidence, eyewitness testimony, and recovery of the murder weapon. The defense argued self-defense. The court convicted the accused based on overwhelming evidence and sentenced to life imprisonment.",
        "outcome": "Convicted - Life Imprisonment",
        "key_sections": "IPC Section 302 (Murder), Section 34 (Common Intention), Evidence Act Section 27",
        "court": "Sessions Court, Delhi",
        "year": 2020
    },
    {
        "case_number": "CRL/2019/045",
        "case_type": "Criminal",
        "title": "State vs. Mohan Singh - Cheating under Section 420 IPC",
        "description": "The accused defrauded multiple investors by running a ponzi scheme promising high returns. Total fraud amount exceeded 5 crores. Investigation revealed systematic cheating through false promises and forged documents. Court found the accused guilty of cheating and criminal conspiracy.",
        "outcome": "Convicted - 7 years rigorous imprisonment + fine of Rs. 50 lakhs",
        "key_sections": "IPC Section 420 (Cheating), Section 120B (Criminal Conspiracy)",
        "court": "Economic Offences Court, Mumbai",
        "year": 2019
    },
    {
        "case_number": "CRL/2021/089",
        "case_type": "Criminal",
        "title": "State vs. Aarti Sharma - Dowry Death under Section 304B IPC",
        "description": "The accused husband and in-laws were charged with dowry death after the victim committed suicide within 7 years of marriage. Evidence showed continuous harassment for additional dowry. Suicide note mentioned cruelty by in-laws. Court convicted all accused based on Section 113B presumption.",
        "outcome": "Convicted - 10 years imprisonment for husband, 7 years for in-laws",
        "key_sections": "IPC Section 304B (Dowry Death), Section 498A (Cruelty), Section 113B Evidence Act",
        "court": "Sessions Court, Jaipur",
        "year": 2021
    },
    {
        "case_number": "CRL/2018/156",
        "case_type": "Criminal",
        "title": "State vs. Ravi Verma - Cybercrime under IT Act",
        "description": "The accused hacked into victim's email and bank accounts, stealing sensitive data and siphoning funds totaling Rs. 15 lakhs. Digital forensics traced the IP addresses and recovery of stolen data. Court convicted under IT Act provisions for unauthorized access and data theft.",
        "outcome": "Convicted - 5 years imprisonment + Rs. 10 lakh fine",
        "key_sections": "IT Act Section 66, Section 66C (Identity Theft), Section 66D (Cheating by Personation)",
        "court": "Cyber Crime Court, Bengaluru",
        "year": 2018
    },
    {
        "case_number": "CRL/2022/023",
        "case_type": "Criminal",
        "title": "State vs. Prakash Reddy - Rape under Section 376 IPC",
        "description": "The accused was charged with rape of a minor. Medical evidence confirmed sexual assault. Victim's testimony was consistent and credible. DNA evidence matched the accused. Court convicted under POCSO Act provisions along with IPC Section 376.",
        "outcome": "Convicted - 20 years rigorous imprisonment + Rs. 5 lakh compensation to victim",
        "key_sections": "IPC Section 376 (Rape), POCSO Act Section 4, Section 6",
        "court": "Special POCSO Court, Hyderabad",
        "year": 2022
    },
]

# Add more cases dynamically
def generate_more_cases():
    """Generate additional 45 cases across different types"""
    additional_cases = []
    
    # Criminal cases (10 more)
    criminal_scenarios = [
        ("Theft", "Section 379 IPC", "Property theft case with recovery of stolen goods"),
        ("Assault", "Section 323/324 IPC", "Grievous hurt case with medical evidence"),
        ("Kidnapping", "Section 363 IPC", "Kidnapping for ransom with rescue"),
        ("Drug Trafficking", "NDPS Act", "Possession and sale of contraband substances"),
        ("Forgery", "Section 467/471 IPC", "Forged documents in property transaction"),
        ("Domestic Violence", "Section 498A IPC", "Cruelty and harassment by husband"),
        ("Bribery", "Prevention of Corruption Act", "Acceptance of bribe by public servant"),
        ("Extortion", "Section 384 IPC", "Threatening for money extraction"),
        ("Robbery", "Section 392 IPC", "Robbery at gunpoint with injuries"),
        ("Culpable Homicide", "Section 304 IPC", "Death not amounting to murder")
    ]
    
    for i, (crime, sections, desc) in enumerate(criminal_scenarios, 6):
        additional_cases.append({
            "case_number": f"CRL/20{18+i%5}/{100+i}",
            "case_type": "Criminal",
            "title": f"State vs. Defendant{i} - {crime}",
            "description": f"{desc}. Evidence presented including witness testimony and forensic reports. Court proceedings concluded with conviction based on established facts and applicable law.",
            "outcome": f"Convicted - {random.choice(['3 years', '5 years', '7 years', '10 years'])} imprisonment",
            "key_sections": sections,
            "court": random.choice(["Sessions Court Delhi", "District Court Mumbai", "High Court Kolkata"]),
            "year": 2018 + i % 5
        })
    
    # Civil cases (15)
    civil_scenarios = [
        ("Breach of Contract", "Contract Act Section 73", "Supplier failed to deliver goods"),
        ("Property Dispute", "Transfer of Property Act", "Ownership dispute over ancestral property"),
        ("Partition Suit", "Hindu Succession Act", "Division of joint family property"),
        ("Specific Performance", "Specific Relief Act Section 10", "Enforcement of sale agreement"),
        ("Injunction", "Code of Civil Procedure Order 39", "Restraining unauthorized construction"),
        ("Defamation", "IPC Section 499/500", "Publication of defamatory content"),
        ("Trespass", "Torts Law", "Unauthorized entry and damage to property"),
        ("Nuisance", "Torts Law", "Noise pollution from commercial establishment"),
        ("Easement Rights", "Easements Act", "Right of way dispute"),
        ("Recovery of Money", "CPC Order 37", "Loan recovery with promissory note"),
        ("Declaration Suit", "Specific Relief Act", "Declaration of title ownership"),
        ("Mesne Profits", "CPC Section 2(12)", "Compensation for wrongful possession"),
        ("Cancellation of Deed", "Registration Act", "Fraudulent sale deed cancellation"),
        ("Partition by Sale", "Partition Act", "Sale of property for division"),
        ("Easement by Prescription", "Easements Act Section 15", "Acquired right through long use")
    ]
    
    for i, (case_type_desc, sections, desc) in enumerate(civil_scenarios, 1):
        additional_cases.append({
            "case_number": f"CIV/20{17+i%6}/{200+i}",
            "case_type": "Civil",
            "title": f"Plaintiff{i} vs. Defendant{i} - {case_type_desc}",
            "description": f"Civil suit filed for {desc}. Evidence including documents, expert testimony, and site inspection reports. Court decreed in favor of plaintiff with detailed reasoning on applicable law.",
            "outcome": random.choice([
                "Decree granted with costs",
                "Partial decree - 70% claim allowed",
                "Suit dismissed - lack of evidence",
                "Decree with specific performance ordered",
                "Injunction granted permanently"
            ]),
            "key_sections": sections,
            "court": random.choice(["Civil Court Delhi", "District Court Chennai", "High Court Mumbai"]),
            "year": 2017 + i % 6
        })
    
    # Corporate/Commercial cases (10)
    corporate_scenarios = [
        ("Trademark Infringement", "Trademarks Act Section 29", "Unauthorized use of registered mark"),
        ("Copyright Violation", "Copyright Act Section 51", "Piracy of creative content"),
        ("Company Insolvency", "IBC 2016", "Insolvency resolution process"),
        ("Shareholder Dispute", "Companies Act Section 241", "Oppression and mismanagement"),
        ("Breach of NDA", "Contract Act", "Disclosure of confidential information"),
        ("Patent Infringement", "Patents Act Section 48", "Unauthorized use of patented invention"),
        ("Unfair Competition", "Competition Act", "Anti-competitive practices"),
        ("Corporate Fraud", "Companies Act Section 447", "Fraudulent financial statements"),
        ("Director Liability", "Companies Act Section 166", "Breach of fiduciary duties"),
        ("Merger Dispute", "Companies Act Section 230", "Scheme of amalgamation challenged")
    ]
    
    for i, (case_desc, sections, desc) in enumerate(corporate_scenarios, 1):
        additional_cases.append({
            "case_number": f"CORP/20{19+i%4}/{300+i}",
            "case_type": "Corporate",
            "title": f"Company{i} vs. Company{i+1} - {case_desc}",
            "description": f"Commercial dispute involving {desc}. Documentary evidence, expert opinions on corporate law, and financial analysis presented. Tribunal/Court ruled based on corporate governance principles.",
            "outcome": random.choice([
                "Injunction granted + Rs. 50 lakh damages",
                "Settlement reached - consent decree",
                "Petition dismissed",
                "Rs. 1 crore compensation awarded",
                "Criminal complaint recommended"
            ]),
            "key_sections": sections,
            "court": random.choice(["NCLT Mumbai", "Company Law Board Delhi", "High Court Bengaluru"]),
            "year": 2019 + i % 4
        })
    
    # Family Law cases (5)
    family_scenarios = [
        ("Divorce - Cruelty", "Hindu Marriage Act Section 13(1)(ia)", "Persistent cruelty by spouse"),
        ("Child Custody", "Guardians and Wards Act", "Best interest of minor child"),
        ("Maintenance", "CrPC Section 125", "Wife seeking monthly maintenance"),
        ("Adoption", "Hindu Adoptions Act", "Legal adoption of minor"),
        ("Restitution of Conjugal Rights", "HMA Section 9", "Spouse withdrew from society")
    ]
    
    for i, (case_desc, sections, desc) in enumerate(family_scenarios, 1):
        additional_cases.append({
            "case_number": f"FAM/20{20+i}/{400+i}",
            "case_type": "Family",
            "title": f"Spouse{i} vs. Spouse{i+1} - {case_desc}",
            "description": f"Family law matter concerning {desc}. Evidence of matrimonial conduct, welfare reports, and counseling records. Court passed orders considering welfare of parties and children.",
            "outcome": random.choice([
                "Divorce decree granted",
                "Custody awarded to mother + Rs. 25,000/month",
                "Maintenance of Rs. 30,000/month awarded",
                "Adoption order passed",
                "Restitution decree granted"
            ]),
            "key_sections": sections,
            "court": "Family Court",
            "year": 2020 + i
        })
    
    # Labor/Employment cases (5)
    labor_scenarios = [
        ("Wrongful Termination", "Industrial Disputes Act", "Termination without due process"),
        ("Sexual Harassment", "POSH Act 2013", "Workplace sexual harassment complaint"),
        ("Wage Dispute", "Payment of Wages Act", "Non-payment of wages and overtime"),
        ("Unfair Labor Practice", "IDA Section 25T", "Discrimination in promotion"),
        ("Workmen Compensation", "Workmen Compensation Act", "Death during employment")
    ]
    
    for i, (case_desc, sections, desc) in enumerate(labor_scenarios, 1):
        additional_cases.append({
            "case_number": f"LAB/20{21+i%3}/{500+i}",
            "case_type": "Labor",
            "title": f"Employee{i} vs. Employer{i} - {case_desc}",
            "description": f"Labor dispute filed for {desc}. Evidence of employment records, witness statements from colleagues, and company policies. Tribunal awarded relief based on labor law principles.",
            "outcome": random.choice([
                "Reinstatement ordered + full back wages",
                "Compensation of Rs. 10 lakhs awarded",
                "Complaint upheld - employer penalized",
                "Settlement - Rs. 5 lakhs ex-gratia",
                "Compensation of Rs. 15 lakhs to legal heirs"
            ]),
            "key_sections": sections,
            "court": "Labor Court",
            "year": 2021 + i % 3
        })
    
    return additional_cases

if __name__ == "__main__":
    with app.app_context():
        print("=" * 80)
        print("F11: LEGAL PRECEDENT ENGINE - SEEDING HISTORICAL CASES")
        print("=" * 80)
        
        # Clear existing historical cases
        print("\n1. Clearing existing historical cases...")
        HistoricalCase.query.delete()
        db.session.commit()
        print("   ✓ Cleared")
        
        # Combine all cases
        all_cases = HISTORICAL_CASES + generate_more_cases()
        
        print(f"\n2. Adding {len(all_cases)} historical cases...")
        
        for case_data in all_cases:
            case = HistoricalCase(
                case_number=case_data["case_number"],
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                outcome=case_data["outcome"],
                key_sections=case_data["key_sections"],
                court=case_data["court"],
                judgment_date=datetime(case_data["year"], random.randint(1, 12), random.randint(1, 28)),
                relevance_score=0.0
            )
            db.session.add(case)
        
        db.session.commit()
        print(f"   ✓ Added {len(all_cases)} cases")
        
        # Display summary
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE - SUMMARY")
        print("=" * 80)
        
        for case_type in ["Criminal", "Civil", "Corporate", "Family", "Labor"]:
            count = HistoricalCase.query.filter_by(case_type=case_type).count()
            print(f"  {case_type:12} : {count:2} cases")
        
        print(f"\n  {'TOTAL':12} : {HistoricalCase.query.count():2} cases")
        print("\n✓ Database seeded successfully!")
        print("✓ Ready for FAISS indexing and precedent search!")
