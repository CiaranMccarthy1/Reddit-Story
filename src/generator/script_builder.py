import re

class ScriptBuilder:
    def __init__(self):
        pass

    def parse_response(self, raw_text):
        """
        Splits the raw AI response into the Story text and the Timestamped lines.
        """
        print("Parsing script...")
        
     
        sections = raw_text.split("SECTION 2: TIMESTAMPED SCRIPT")
        
        if len(sections) < 2:
   
            story_text = sections[0].replace("SECTION 1: STORY", "").strip()
            return story_text, []

        story_text = sections[0].replace("SECTION 1: STORY", "").strip()
        script_block = sections[1].strip()

        parsed_script = []
        lines = script_block.split('\n')
        
        # More flexible pattern: 
        # - Handles optional quotes
        # - Handles different spacing
        pattern = r'^\s*(\d{2}):(\d{2}):(\d{2}):\s*["\']?(.*?)["\']?$'

        print(f"DEBUG: Processing {len(lines)} lines from AI response...")

        for line in lines:
            line = line.strip()
            if not line: continue

            match = re.search(pattern, line)
            
            if match:
                h, m, s = map(int, match.groups()[:3])
                total_seconds = h * 3600 + m * 60 + s
                
                text_content = match.group(4).strip()
                
                parsed_script.append({"start": total_seconds, "text": text_content})
        
        print(f"DEBUG: Successfully parsed {len(parsed_script)} lines.")
        if len(parsed_script) < 5 and len(lines) > 10:
             print("WARNING: Parsed significantly fewer lines than input. Regex might be failing.")
             for i, l in enumerate(lines[:3]): print(f"Sample Line {i}: {l}")

        return story_text, parsed_script