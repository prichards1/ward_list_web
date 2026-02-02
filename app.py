import os
import secrets
import io
import csv
import re
import random
import jellyfish
from flask import Flask, render_template, request, redirect, url_for, session, flash
from thefuzz import process, fuzz

app = Flask(__name__)
# Load from Environment variable, fallback to dev key if missing
# Falls back if the key is missing OR if it is empty
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)

# --- LOGIC CLASS (Unchanged) ---
class NameMatcher:
    def __init__(self, correct_names):
        self.correct_names = correct_names
        self.phonetic_map = {}
        for name in correct_names:
            code = jellyfish.metaphone(name)
            if code not in self.phonetic_map:
                self.phonetic_map[code] = []
            self.phonetic_map[code].append(name)

        self.nickname_db = {
            "dave": ["david"], "dan": ["daniel"], "danny": ["daniel"], "brad": ["bradley"],
            "bob": ["robert"], "bobby": ["robert"], "rob": ["robert"],
            "bill": ["william"], "will": ["william"], "billy": ["william"],
            "peggy": ["margaret"], "maggie": ["margaret"], "maddy": ["madeline"],
            "liz": ["elizabeth"], "beth": ["elizabeth", "bethany"], "lizzy": ["elizabeth"],
            "chris": ["christopher", "christina", "christine"],
            "mike": ["michael"], "mikey": ["michael"], "max": ["maxwell"],
            "matt": ["matthew"], "debbie": ["debra"], "jake": ["jacob"],
            "jen": ["jennifer"], "jenny": ["jennifer"],
            "joe": ["joseph"], "joey": ["joseph"], "jim": ["james"],
            "tom": ["thomas"], "tommy": ["thomas"],
            "brooke": ["brooklyn"], "steph": ["stephanie"],
            "zach": ["zachary"], "kim": ["kimberly"], "alex": ["alexander", "alexandra"]
        }

    def find_match(self, user_guess):
        guess_clean = user_guess.strip()
        guess_lower = guess_clean.lower()
        if not guess_clean: return None, None

        # 1. Exact
        for name in self.correct_names:
            if name.lower() == guess_lower:
                return name, "Exact Match"

        # 2. Nickname
        possible_formal_names = self.nickname_db.get(guess_lower, [])
        for formal in possible_formal_names:
            for target_name in self.correct_names:
                if target_name.lower() == formal:
                    return target_name, "Nickname Match"

        # 3. Phonetic
        guess_phonetic = jellyfish.metaphone(guess_clean)
        if guess_phonetic in self.phonetic_map:
            return self.phonetic_map[guess_phonetic][0], "Phonetic Match"

        # 4. Fuzzy
        best_match = process.extractOne(guess_clean, self.correct_names, scorer=fuzz.ratio)
        if best_match:
            name_found, score = best_match
            if score >= 80:
                return name_found, f"Typo Fix ({score}%)"

        return None, None

def clean_header_key(key):
    if key is None: return ""
    cleaned = re.sub(r'[^\w\s-]', '', key)
    return cleaned.strip()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files: return redirect(request.url)
        file = request.files['file']
        if file.filename == '': return redirect(request.url)
        
        if file:
            try:
                stream_content = file.stream.read().decode("utf-8")
            except UnicodeDecodeError:
                file.stream.seek(0)
                stream_content = file.stream.read().decode("latin-1")

            stream = io.StringIO(stream_content, newline=None)
            csv_input = csv.DictReader(stream)
            field_map = {clean_header_key(name): name for name in csv_input.fieldnames if name}
            
            required = ["Last Name", "First Name"]
            if any(f not in field_map for f in required):
                flash(f"Error: Missing columns. Found: {list(field_map.keys())}")
                return redirect(request.url)

            grouped_families = {}
            for row in csv_input:
                ln = row.get(field_map["Last Name"], "").strip()
                fn = row.get(field_map["First Name"], "").strip()
                if ln and fn:
                    if ln not in grouped_families: grouped_families[ln] = []
                    grouped_families[ln].append(fn)
            
            families = []
            for ln, fns in grouped_families.items():
                families.append({'Last Name': ln, 'First Name': fns})
            
            session['families'] = families
            session['score'] = 0
            session['total_attempts'] = 0
            
            # Reset Quiz State
            session.pop('current_family', None) 
            session.pop('results', None)
            
            return redirect(url_for('quiz'))

    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'families' not in session: return redirect(url_for('home'))

    # Initialize a new family if needed
    if 'current_family' not in session:
        session['current_family'] = random.choice(session['families'])
        session['results'] = None # Clear old results

    # Get easy access variables
    family = session['current_family']
    correct_names = family['First Name'] # This is a LIST now
    
    # Handle Form Submission (User clicked "Submit Guesses" or "Next Family")
    if request.method == 'POST':
        action = request.form.get('action')

        # --- CASE 1: User is Submitting Guesses ---
        if action == 'submit':
            raw_input = request.form.get('guesses', '')
            user_lines = raw_input.split('\n')
            
            matcher = NameMatcher(correct_names)
            
            matched_results = [] # format: (real_name, user_guess, reason)
            extra_guesses = []
            
            # We track found names to calculate missed ones later
            found_names_set = set()

            for line in user_lines:
                guess = line.strip()
                if not guess: continue
                
                match_name, reason = matcher.find_match(guess)
                
                if match_name:
                    # Avoid duplicate credits for the same name
                    if match_name not in found_names_set:
                        matched_results.append({'real': match_name, 'guess': guess, 'reason': reason})
                        found_names_set.add(match_name)
                    else:
                        extra_guesses.append(guess + " (Duplicate)")
                else:
                    extra_guesses.append(guess)

            # Calculate missed names
            missed_names = [n for n in correct_names if n not in found_names_set]

            # Update Score
            if len(missed_names) == 0 and len(extra_guesses) == 0:
                session['score'] += 1
            session['total_attempts'] += 1

            # Save Results to Session so we can render them
            session['results'] = {
                'matched': matched_results,
                'missed': missed_names,
                'extra': extra_guesses,
                'is_perfect': (len(missed_names) == 0 and len(extra_guesses) == 0)
            }
            
            # Render the same page, but now the template will see 'results' is not None
            return render_template('quiz.html', family=family, results=session['results'], score=session['score'], total=session['total_attempts'])

        # --- CASE 2: User clicked "Next Family" ---
        elif action == 'next':
            session.pop('current_family', None)
            session.pop('results', None)
            return redirect(url_for('quiz'))

    # GET Request: Just show the form
    return render_template('quiz.html', family=family, results=session.get('results'), score=session['score'], total=session['total_attempts'])

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('home'))

# Add this new route to app.py
@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

if __name__ == '__main__':
    app.run(debug=True)