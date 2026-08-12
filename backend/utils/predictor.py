import json
import math
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

class CollegePredictor:
    """Handles college prediction logic for Tamil Nadu colleges"""
    
    def __init__(self):
        self.cutoff_multipliers = {
            "ENGINEERING": 1.0,
            "SCIENCE": 1.0,
            "ARTS": 1.0,
            "COMMERCE": 1.0
        }
        self.community_relaxations = {
            "OC": 0,
            "BC": 3.5,
            "MBC": 5.5,
            "SC": 12.5,
            "ST": 18.5
        }
        self.colleges_data = self._load_college_data()
    
    def _load_college_data(self) -> List[Dict]:
        """Load college data from JSON file"""
        data_folder = Path(__file__).resolve().parent.parent / 'data'
        candidate_files = [
            data_folder / 'tamilnadu_colleges.json',
            data_folder / 'colleges.json',
            data_folder / 'college.json'
        ]

        for file_path in candidate_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except FileNotFoundError:
                continue
            except json.JSONDecodeError:
                continue

        # Return sample data if no file exists or the JSON is invalid
        return self._get_sample_colleges()
    
    def _get_sample_colleges(self) -> List[Dict]:
        """Return sample college data if no JSON file is found"""
        return [
            {
                "college_name": "Anna University Chennai",
                "branch_name": "Computer Science Engineering",
                "cutoff_2023": 198.5,
                "district": "Chennai",
                "stream": "ENGINEERING",
                "university": "Anna University",
                "college_type": "Government",
                "available_seats": 120,
                "fees_annual": 18000,
                "year_established": 1978,
                "ranking": "Top 5 in Tamil Nadu",
                "placement_percentage": 95,
                "average_package": 1400000,
                "highest_package": 4800000,
                "community_cutoffs": {
                    "OC": 198.5,
                    "BC": 195.0,
                    "MBC": 192.0,
                    "SC": 184.5,
                    "ST": 177.5
                }
            },
            {
                "college_name": "College of Engineering Guindy",
                "branch_name": "Computer Science Engineering",
                "cutoff_2023": 200.0,
                "district": "Chennai",
                "stream": "ENGINEERING",
                "university": "Anna University",
                "college_type": "Government",
                "available_seats": 120,
                "fees_annual": 15000,
                "year_established": 1794,
                "ranking": "Top 5 in Tamil Nadu",
                "placement_percentage": 95,
                "average_package": 1200000,
                "highest_package": 4500000,
                "community_cutoffs": {
                    "OC": 200.0,
                    "BC": 196.5,
                    "MBC": 193.5,
                    "SC": 186.0,
                    "ST": 179.0
                }
            },
            {
                "college_name": "PSG College of Technology",
                "branch_name": "Computer Science Engineering",
                "cutoff_2023": 197.5,
                "district": "Coimbatore",
                "stream": "ENGINEERING",
                "university": "Anna University",
                "college_type": "Private",
                "available_seats": 120,
                "fees_annual": 180000,
                "year_established": 1951,
                "ranking": "Top 5 in Tamil Nadu",
                "placement_percentage": 95,
                "average_package": 1500000,
                "highest_package": 5000000,
                "community_cutoffs": {
                    "OC": 197.5,
                    "BC": 194.0,
                    "MBC": 191.0,
                    "SC": 183.5,
                    "ST": 176.5
                }
            },
            {
                "college_name": "Loyola College",
                "branch_name": "B.Sc Computer Science",
                "cutoff_2023": 190.0,
                "district": "Chennai",
                "stream": "SCIENCE",
                "university": "University of Madras",
                "college_type": "Private",
                "available_seats": 80,
                "fees_annual": 40000,
                "year_established": 1925,
                "ranking": "Top 5 in Tamil Nadu",
                "placement_percentage": 85,
                "average_package": 800000,
                "highest_package": 2800000,
                "community_cutoffs": {
                    "OC": 190.0,
                    "BC": 186.5,
                    "MBC": 183.5,
                    "SC": 176.0,
                    "ST": 169.0
                }
            },
            {
                "college_name": "Presidency College",
                "branch_name": "B.Sc Mathematics",
                "cutoff_2023": 192.0,
                "district": "Chennai",
                "stream": "SCIENCE",
                "university": "University of Madras",
                "college_type": "Government",
                "available_seats": 50,
                "fees_annual": 5000,
                "year_established": 1840,
                "ranking": "Top 5 in Tamil Nadu",
                "placement_percentage": 80,
                "average_package": 700000,
                "highest_package": 2600000,
                "community_cutoffs": {
                    "OC": 192.0,
                    "BC": 188.5,
                    "MBC": 185.5,
                    "SC": 178.0,
                    "ST": 171.0
                }
            }
        ]
    
    def calculate_cutoff(
        self,
        mathematics: float,
        physics: float,
        chemistry: float,
        stream: str = 'ENGINEERING',
        optional_subject: float = 0,
    ) -> float:
        """
        Calculate admission score based on Tamil Nadu +2 major subject pattern.

        Engineering: Maths + (Physics / 2) + (Chemistry / 2) = cutoff out of 200.
        Science / Arts: Physics + Chemistry + Maths/Biology + Optional = score out of 400.
        Commerce: Accountancy + Commerce + Economics + Business Maths/CS/Auditing = score out of 400.
        """
        stream = (stream or 'ENGINEERING').upper()
        if stream == 'ENGINEERING':
            cutoff = mathematics + (physics / 2) + (chemistry / 2)
        else:
            cutoff = mathematics + physics + chemistry + optional_subject

        return round(cutoff, 2)
    
    def get_community_cutoff(self, community: str, cutoff_score: float) -> float:
        """
        Apply community relaxation to cutoff score
        """
        relaxation = self.community_relaxations.get(community, 0)
        return round(cutoff_score + relaxation, 2)
    
    def match_colleges(self, cutoff_score: float, community: str, stream: str) -> Dict:
        """
        Match colleges based on cutoff score, community, and stream
        
        Returns categorized colleges: safe, borderline, dream
        """
        if not self.colleges_data:
            return {
                'safe': [],
                'borderline': [],
                'dream': [],
                'total_matched': 0
            }
        
        safe_colleges = []
        borderline_colleges = []
        dream_colleges = []
        
        # Apply community relaxation
        effective_cutoff = self.get_community_cutoff(community, cutoff_score)
        
        for college in self.colleges_data:
            # Check if college exists
            if not college:
                continue
            
            # Check stream match (case insensitive)
            college_stream = college.get('stream', '').upper()
            if college_stream != stream.upper():
                continue
            
            # Get community specific cutoff
            community_cutoffs = college.get('community_cutoffs', {})
            if community in community_cutoffs:
                college_cutoff = community_cutoffs[community]
            else:
                # Fallback to general cutoff
                college_cutoff = college.get('cutoff_2023', 0)
            
            if college_cutoff == 0:
                continue
            
            # Calculate difference
            diff = effective_cutoff - college_cutoff
            
            # Create college data object
            college_data = {
                'college_name': college.get('college_name', 'Unknown College'),
                'branch_name': college.get('branch_name', 'Unknown Branch'),
                'district': college.get('district', 'Unknown District'),
                'stream': college.get('stream', stream),
                'university': college.get('university', 'Unknown University'),
                'college_type': college.get('college_type', 'Unknown'),
                'closing_cutoff': college_cutoff,
                'available_seats': college.get('available_seats', 0),
                'cutoff_difference': round(diff, 2),
                'fees_annual': college.get('fees_annual', 0),
                'year_established': college.get('year_established', 0),
                'ranking': college.get('ranking', 'Not Ranked'),
                'placement_percentage': college.get('placement_percentage', 0),
                'average_package': college.get('average_package', 0),
                'highest_package': college.get('highest_package', 0),
                'counselling_code': college.get('counselling_code', 'N/A'),
                'apply_link': college.get('apply_link', '#'),
                'admission_mode': college.get('admission_mode', 'Counselling / institution admission')
            }
            
            # Categorize based on difference
            if diff >= 2.0:
                college_data['probability'] = 'High Chance'
                college_data['category'] = 'Safe'
                safe_colleges.append(college_data)
            elif -2.0 <= diff < 2.0:
                college_data['probability'] = 'Moderate Chance'
                college_data['category'] = 'Borderline'
                borderline_colleges.append(college_data)
            elif -5.0 <= diff < -2.0:
                college_data['probability'] = 'Low Chance'
                college_data['category'] = 'Dream'
                dream_colleges.append(college_data)
            # Colleges with diff < -5.0 are not recommended
        
        # Sort by cutoff difference (descending)
        safe_colleges.sort(key=lambda x: x['cutoff_difference'], reverse=True)
        borderline_colleges.sort(key=lambda x: x['cutoff_difference'], reverse=True)
        dream_colleges.sort(key=lambda x: x['cutoff_difference'], reverse=True)
        
        return {
            'safe': safe_colleges[:10],  # Limit to top 10
            'borderline': borderline_colleges[:10],
            'dream': dream_colleges[:10],
            'total_matched': len(safe_colleges) + len(borderline_colleges) + len(dream_colleges),
            'effective_cutoff': effective_cutoff
        }
    
    def get_college_by_name(self, college_name: str) -> Optional[Dict]:
        """Get college details by name"""
        for college in self.colleges_data:
            if college.get('college_name', '').lower() == college_name.lower():
                return college
        return None
    
    def get_colleges_by_district(self, district: str) -> List[Dict]:
        """Get all colleges in a district"""
        return [c for c in self.colleges_data if c.get('district', '').lower() == district.lower()]
    
    def get_colleges_by_stream(self, stream: str) -> List[Dict]:
        """Get all colleges in a stream"""
        return [c for c in self.colleges_data if c.get('stream', '').upper() == stream.upper()]
    
    def get_statistics(self) -> Dict:
        """Get statistics about the college database"""
        total = len(self.colleges_data)
        streams = {}
        districts = {}
        college_types = {}
        
        for college in self.colleges_data:
            stream = college.get('stream', 'Unknown')
            streams[stream] = streams.get(stream, 0) + 1
            
            district = college.get('district', 'Unknown')
            districts[district] = districts.get(district, 0) + 1
            
            college_type = college.get('college_type', 'Unknown')
            college_types[college_type] = college_types.get(college_type, 0) + 1
        
        return {
            'total_colleges': total,
            'streams': streams,
            'districts': districts,
            'college_types': college_types
        }


class ChatbotAssistant:
    """Handles chatbot responses for college counselling"""
    
    def __init__(self, predictor: Optional[CollegePredictor] = None):
        self.predictor = predictor or CollegePredictor()
        self.responses = {
            'cutoff': self._handle_cutoff_query,
            'college': self._handle_college_query,
            'strategy': self._handle_strategy_query,
            'district': self._handle_district_query,
            'stream': self._handle_stream_query,
            'default': self._handle_default
        }
    
    def get_response(self, message: str) -> str:
        """
        Generate response based on user message
        """
        message_lower = message.lower()
        
        # Detect intent
        if any(word in message_lower for word in ['cutoff', 'score', 'marks', 'calculate']):
            return self._handle_cutoff_query(message)
        elif any(word in message_lower for word in ['college', 'branch', 'course', 'seat', 'admission']):
            return self._handle_college_query(message)
        elif any(word in message_lower for word in ['strategy', 'preference', 'fill', 'order', 'tips']):
            return self._handle_strategy_query(message)
        elif any(word in message_lower for word in ['district', 'city', 'place', 'location']):
            return self._handle_district_query(message)
        elif any(word in message_lower for word in ['stream', 'engineering', 'science', 'arts']):
            return self._handle_stream_query(message)
        else:
            return self._handle_default(message)
    
    def _handle_cutoff_query(self, message: str) -> str:
        """Handle questions about cutoffs"""
        return """
        📊 **Understanding Cutoffs in Tamil Nadu:**
        
        🎯 **Cutoff Score Calculation:**
        • Engineering: Maths + (Physics ÷ 2) + (Chemistry ÷ 2) = cutoff out of 200
        • Science / Arts: Physics + Chemistry + Maths/Biology + Optional = score out of 400
        • Commerce: Accountancy + Commerce + Economics + Business Maths/CS/Auditing = score out of 400
        
        🏷️ **Community Relaxations:**
        • OC: No relaxation
        • BC: +3.5 marks
        • MBC: +5.5 marks
        • SC: +12.5 marks
        • ST: +18.5 marks
        
        📈 **Top College Cutoffs (2023):**
        • CSE at CEG: 200.0 (OC)
        • CSE at MIT: 199.0 (OC)
        • CSE at Anna University: 198.5 (OC)
        • CSE at PSG Tech: 197.5 (OC)
        • CSE at SSN: 197.0 (OC)
        
        💡 **Tip:** Higher cutoff score = Better chance at top colleges!
        """
    
    def _handle_college_query(self, message: str) -> str:
        """Handle questions about colleges"""
        return """
        🎓 **Top Engineering Colleges in Tamil Nadu:**
        
        🏛️ **Government Colleges:**
        • College of Engineering Guindy (CEG)
        • Madras Institute of Technology (MIT)
        • Anna University Chennai
        • Government College of Technology, Coimbatore
        • Government College of Engineering, Salem
        
        🏛️ **Top Private Colleges:**
        • PSG College of Technology, Coimbatore
        • SSN College of Engineering, Chennai
        • Thiagarajar College of Engineering, Madurai
        • Kongu Engineering College, Erode
        • Mepco Schlenk Engineering College, Virudhunagar
        
        🏛️ **Deemed Universities:**
        • VIT University, Vellore
        • SRM Institute of Science and Technology
        • SASTRA University, Thanjavur
        • Amrita School of Engineering
        • Sathyabama Institute of Science and Technology
        
        🧪 **Top Science Colleges:**
        • Loyola College, Chennai
        • Presidency College, Chennai
        • Madras Christian College, Chennai
        • Stella Maris College, Chennai
        • St. Joseph's College, Trichy
        
        Use the predictor tool above to find your personalized matches!
        """
    
    def _handle_strategy_query(self, message: str) -> str:
        """Handle questions about preference strategy"""
        return """
        🎯 **Smart Preference Filling Strategy:**
        
        📊 **Recommended Distribution:**
        • **25-30%** Dream Choices (Aspirational)
        • **40-50%** Borderline Options (Realistic)
        • **20-30%** Safe Choices (Backup)
        
        📝 **Filling Order:**
        1️⃣ Dream Colleges (High ambition, 2-5 points above your score)
        2️⃣ Borderline Colleges (Good balance, ±2 points of your score)
        3️⃣ Safe Colleges (Secure admission, 2+ points below your score)
        
        💡 **Pro Tips:**
        • Don't fill all top choices first
        • Include at least 5-6 safe options
        • Research branch preferences carefully
        • Consider location and placement records
        • Check fee structure and scholarships
        • Look at college infrastructure and faculty
        
        🎯 **Tamil Nadu Specific Tips:**
        • Tamil Nadu Engineering Admissions (TNEA) has 7 rounds
        • Anna University counseling is the main process
        • Government quota and management quota are separate
        • Community certificates must be valid
        • Keep original documents ready for verification
        
        **Remember:** Every preference counts in counseling!
        """
    
    def _handle_district_query(self, message: str) -> str:
        """Handle questions about districts"""
        stats = self.predictor.get_statistics()
        districts = stats.get('districts', {})
        
        # Get top districts
        top_districts = sorted(districts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        response = "📍 **Colleges by District in Tamil Nadu:**\n\n"
        for district, count in top_districts:
            response += f"• **{district}**: {count} colleges\n"
        
        response += f"\nTotal colleges across {len(districts)} districts: {stats.get('total_colleges', 0)}"
        
        return response
    
    def _handle_stream_query(self, message: str) -> str:
        """Handle questions about streams"""
        stats = self.predictor.get_statistics()
        streams = stats.get('streams', {})
        
        response = "📚 **Colleges by Stream:**\n\n"
        for stream, count in streams.items():
            response += f"• **{stream}**: {count} colleges\n"
        
        return response
    
    def _handle_default(self, message: str) -> str:
        """Default response for general queries"""
        return """
        👋 Welcome to College Counselling Assistant!
        
        I'm here to help you with college admissions in Tamil Nadu.
        
        🤔 **Ask me about:**
        • 📊 **Cutoff calculation** 
          Example: "How is cutoff calculated?"
        
        • 🏫 **College selection** 
          Example: "Which are the top colleges?"
        
        • 🎯 **Preference strategy** 
          Example: "What strategy should I follow?"
        
        • 📍 **Colleges by district**
          Example: "Colleges in Chennai"
        
        • 📚 **Streams available**
          Example: "Engineering colleges"
        
        💡 **Quick Tip:** Use the Predictor tool above for personalized college matching based on your marks and category!
        
        What would you like to know today?
        """