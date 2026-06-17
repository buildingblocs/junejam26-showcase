import random


CHALLENGES = {
    "terminal_python": {
        "role": "Python Engineer",
        "label": "Python Lab",
        "difficulties": {
            "easy": {
                "id": "py_easy_len",
                "title": "Python Length Check",
                "category": "Python Logic",
                "difficulty": "easy",
                "prompt": "What does len(['a', 'b', 'c']) return?",
                "options": ["1", "2", "3", "4"],
                "answers": ["3", "c"],
                "explanation": "len() returns the number of items in a sequence.",
                "hint": "Count the items in the list.",
            },
            "medium": {
                "id": "py_medium_loop",
                "title": "Loop Counter Audit",
                "category": "Python Logic",
                "difficulty": "medium",
                "prompt": "What is printed by: total=0; for n in [1,2,3]: total += n; print(total)",
                "options": ["3", "5", "6", "123"],
                "answers": ["6", "c"],
                "explanation": "The loop adds 1 + 2 + 3, producing 6.",
                "hint": "Track the running total after each loop.",
            },
            "hard": {
                "id": "py_hard_nested",
                "title": "Nested Function Trace",
                "category": "Python Logic",
                "difficulty": "hard",
                "prompt": "What is returned by f(3) if def f(x): return (lambda y: y*x)(x+2)?",
                "options": ["5", "6", "15", "25"],
                "answers": ["15", "c"],
                "explanation": "x is 3, y becomes 5, and 5 * 3 is 15.",
                "hint": "Substitute x first, then evaluate the lambda.",
            },
        },
    },
    "terminal_crypto": {
        "role": "Cryptographer",
        "label": "Pwn Lab",
        "difficulties": {
            "easy": {
                "id": "pwn_easy_nc",
                "title": "Netcat Basics",
                "category": "Pwn Concepts",
                "difficulty": "easy",
                "prompt": "Which command commonly connects to a remote challenge on host example.com port 31337?",
                "options": [
                    "nc example.com 31337",
                    "ssh example.com 31337",
                    "ping example.com 31337",
                    "curl 31337 example.com",
                ],
                "answers": ["nc example.com 31337", "a"],
                "explanation": "netcat is commonly used to connect to TCP challenge services.",
                "hint": "The short command is often called nc.",
            },
            "medium": {
                "id": "pwn_medium_recv",
                "title": "Pwntools Receive",
                "category": "Python for Cybersecurity",
                "difficulty": "medium",
                "prompt": "In pwntools, which method receives data until a marker appears?",
                "options": ["recvuntil()", "sendline()", "p64()", "process()"],
                "answers": ["recvuntil()", "a"],
                "explanation": "recvuntil() reads from the target until the chosen delimiter.",
                "hint": "The method name says it receives until something.",
            },
            "hard": {
                "id": "pwn_hard_pack",
                "title": "Payload Packing",
                "category": "Pwn Concepts",
                "difficulty": "hard",
                "prompt": "Which pwntools helper packs a 64-bit little-endian integer for a payload?",
                "options": ["p32()", "p64()", "u64()", "flatstr()"],
                "answers": ["p64()", "b"],
                "explanation": "p64() packs a value into 64-bit little-endian bytes.",
                "hint": "The helper name includes the target bit width.",
            },
        },
    },
    "terminal_network": {
        "role": "Network Analyst",
        "label": "Reverse Engineering Lab",
        "difficulties": {
            "easy": {
                "id": "rev_easy_return",
                "title": "Return Value",
                "category": "Reverse Engineering",
                "difficulty": "easy",
                "prompt": "In decompiled C, what does `return 0;` usually mean for main()?",
                "options": ["Crash", "Success", "Network error", "Infinite loop"],
                "answers": ["success", "b"],
                "explanation": "A main() return value of 0 conventionally indicates success.",
                "hint": "Think of process exit codes.",
            },
            "medium": {
                "id": "rev_medium_branch",
                "title": "Suspicious Branch",
                "category": "Reverse Engineering",
                "difficulty": "medium",
                "prompt": "A check says `if (strcmp(input, \"open\") == 0)`. Which input passes?",
                "options": ["admin", "open", "0", "strcmp"],
                "answers": ["open", "b"],
                "explanation": "strcmp returns 0 when strings are equal.",
                "hint": "In C, strcmp equality is represented by zero.",
            },
            "hard": {
                "id": "rev_hard_trace",
                "title": "Function Trace",
                "category": "Reverse Engineering",
                "difficulty": "hard",
                "prompt": "If check(x) returns `(x ^ 0x2a) == 0x10`, which x passes?",
                "options": ["0x10", "0x2a", "0x3a", "0x40"],
                "answers": ["0x3a", "c"],
                "explanation": "x must equal 0x10 ^ 0x2a, which is 0x3a.",
                "hint": "XOR both sides by 0x2a.",
            },
        },
    },
}

TERMINAL_TOPICS = {
    "terminal_python": {
        "role": "Python Engineer",
        "category": "Python Basics",
        "system": "Data Center",
        "track": "python basics",
        "defender_focus": "repairing Python automation, validation, and log-processing scripts",
        "attacker_focus": "spotting Python mistakes attackers abuse, such as unsafe eval, leaked secrets, and unsafe deserialization",
    },
    "terminal_crypto": {
        "role": "Cryptographer",
        "category": "Pwn / Binary Exploitation",
        "system": "Network Core",
        "track": "pwn",
        "defender_focus": "hardening network-facing binaries with bounds checks, stack canaries, NX/DEP, ASLR, and safer input handling",
        "attacker_focus": "understanding netcat, pwntools recvuntil, p64 packing, buffer overflows, ROP, and format-string primitives",
    },
    "terminal_network": {
        "role": "Network Analyst",
        "category": "Reverse Engineering",
        "system": "Power Grid",
        "track": "reverse engineering",
        "defender_focus": "reverse-engineering control logic to validate safe firmware and restore operations",
        "attacker_focus": "tracing branches, string checks, and XOR gates to understand bypass paths",
    },
}

CHEATSHEET_TOPICS = {
    "terminal_python": {
        "title": "Python & Secure Automation",
        "summary": (
            "Python logic used in repair scripts, plus unsafe patterns that "
            "expose data or execute attacker input."
        ),
        "topics": (
            (
                "len() and sequences",
                "len() returns the number of items in a sequence.",
            ),
            (
                "Loops and accumulation",
                "Track each iteration and update the running value in order.",
            ),
            (
                "Function and lambda tracing",
                "Substitute arguments first, then evaluate nested calls inside out.",
            ),
            (
                "Secret handling",
                "Never print, log, or commit API keys, passwords, or access tokens.",
            ),
            (
                "Unsafe eval",
                "eval() executes text as Python; never pass it untrusted input.",
            ),
            (
                "Unsafe deserialization",
                "pickle can execute code; never load untrusted pickle data.",
            ),
            (
                "Patching",
                "A patch changes vulnerable code so a known weakness cannot be abused.",
            ),
            (
                "Hashes and integrity",
                "Compare trusted hashes to detect altered files, logs, or code.",
            ),
            (
                "Virtual environments",
                "venv isolates dependencies so repair tools stay reproducible.",
            ),
        ),
    },
    "terminal_crypto": {
        "title": "Pwn & Binary Exploitation",
        "summary": (
            "How memory-corruption attacks work, how exploit scripts communicate, "
            "and which mitigations stop them."
        ),
        "topics": (
            ("netcat (nc)", "Connect to a raw TCP service with: nc HOST PORT."),
            (
                "recvuntil()",
                "Wait for a known prompt before sending the next pwntools payload.",
            ),
            (
                "p64() and packing",
                "Pack a 64-bit integer into little-endian payload bytes.",
            ),
            (
                "Payloads and shellcode",
                "Payloads are crafted data; shellcode is injected machine code.",
            ),
            (
                "Buffer overflows",
                "Writing past a fixed buffer can corrupt data and control flow.",
            ),
            (
                "Bounds checks and fgets",
                "Validate lengths and use size-limited input before copying data.",
            ),
            (
                "Format strings",
                "Use printf(\"%s\", input), never input as the format itself.",
            ),
            (
                "Stack canaries",
                "A checked stack value detects overwrites before return.",
            ),
            (
                "NX / DEP",
                "Mark data memory non-executable to block injected shellcode.",
            ),
            (
                "ASLR and address leaks",
                "Randomized addresses hinder exploits; leaks reveal the layout.",
            ),
            (
                "ROP",
                "Chain existing code gadgets when injected code cannot execute.",
            ),
        ),
    },
    "terminal_network": {
        "title": "Reverse Engineering",
        "summary": (
            "Read compiled program behavior, validate firmware integrity, and "
            "trace checks that control hardware."
        ),
        "topics": (
            (
                "Process return values",
                "main returning 0 conventionally means successful execution.",
            ),
            (
                "strcmp checks",
                "strcmp returns 0 for equal strings, so checks often test == 0.",
            ),
            (
                "XOR branches",
                "Apply the same XOR mask again to recover the original value.",
            ),
            (
                "Firmware integrity",
                "Verify firmware against a known-good hash before restoration.",
            ),
            (
                "Checksums",
                "A checksum summarizes bytes so changes can be detected.",
            ),
            (
                "Strings analysis",
                "Readable strings can expose URLs, commands, and credentials.",
            ),
            (
                "Control-flow tracing",
                "Follow branches and calls that change safety-critical state.",
            ),
            (
                "Memory-mapped I/O",
                "Special memory writes often reveal hardware-control code.",
            ),
            (
                "Debugging and patching",
                "Step through code, then alter binary checks only in controlled labs.",
            ),
        ),
    },
}

TERMINOLOGY_CHANCE = 0.35

TERMINOLOGY_CHALLENGES = {
    "terminal_python": {
        "repair": [
            {
                "term": "patch",
                "question": "One word: What do defenders apply to fix a known software vulnerability?",
                "aliases": ["patching", "patches"],
                "explanation": "A patch updates vulnerable code so a known weakness can no longer be abused.",
                "hint": "It is a software fix.",
                "relevance": "Patching is one of the most common real-world defense tasks after a vulnerability is found.",
            },
            {
                "term": "hash",
                "question": "One word: What fixed-length fingerprint helps verify that a log or file has not changed?",
                "aliases": ["hashing"],
                "explanation": "A hash is a deterministic fingerprint of data, so changes produce a different value.",
                "hint": "Incident responders compare this fingerprint.",
                "relevance": "Hashes help defenders verify integrity for logs, backups, and deployed code.",
            },
            {
                "term": "venv",
                "question": "One word: What Python environment folder isolates project dependencies?",
                "aliases": ["virtualenv"],
                "explanation": "A venv keeps dependencies isolated so one project does not break another.",
                "hint": "Python projects often create a .venv folder.",
                "relevance": "Isolated environments make repair scripts easier to reproduce and audit.",
            },
        ],
        "attack": [
            {
                "term": "eval",
                "question": "One word: Which Python function executes a string as code and is dangerous with user input?",
                "aliases": [],
                "explanation": "eval() runs text as Python code, so attacker-controlled text can become code execution.",
                "hint": "It evaluates text.",
                "relevance": "Unsafe eval is a classic example of turning user input into executable behavior.",
            },
            {
                "term": "token",
                "question": "One word: What secret value often proves an API request is authorized?",
                "aliases": ["key", "apikey", "api_key"],
                "explanation": "A token is a secret credential used to authorize requests or sessions.",
                "hint": "APIs often send it with requests.",
                "relevance": "Leaked tokens can let attackers impersonate services or users.",
            },
            {
                "term": "pickle",
                "question": "One word: Which Python module is risky when loading untrusted serialized objects?",
                "aliases": [],
                "explanation": "pickle can execute code while recreating Python objects from serialized data.",
                "hint": "It serializes Python objects.",
                "relevance": "Unsafe deserialization is a real attack path in Python services.",
            },
        ],
    },
    "terminal_crypto": {
        "repair": [
            {
                "term": "bounds",
                "question": "One word: What checks stop code from reading or writing past a buffer limit?",
                "aliases": ["bound"],
                "explanation": "Bounds checks compare input length or indexes against valid limits before copying or accessing memory.",
                "hint": "They define the safe limits.",
                "relevance": "Bounds checks are one of the clearest defenses against buffer overflows in network services.",
            },
            {
                "term": "canary",
                "question": "One word: What stack value is checked before return to detect buffer overflows?",
                "aliases": ["cookie"],
                "explanation": "A stack canary changes if an overflow reaches saved control data, causing the program to abort.",
                "hint": "It guards the stack.",
                "relevance": "Canaries are a common binary-hardening mitigation for memory-corruption bugs.",
            },
            {
                "term": "ASLR",
                "question": "One acronym: Which mitigation randomizes memory addresses?",
                "aliases": [],
                "explanation": "ASLR randomizes where code and data live in memory, making exploits less predictable.",
                "hint": "Address Space Layout Randomization.",
                "relevance": "ASLR makes reliable exploitation harder for attackers.",
            },
            {
                "term": "NX",
                "question": "One acronym: Which mitigation marks stack memory as non-executable?",
                "aliases": ["dep"],
                "explanation": "NX prevents injected stack bytes from running as instructions.",
                "hint": "It means non-executable.",
                "relevance": "NX blocks many classic shellcode injection attacks.",
            },
            {
                "term": "DEP",
                "question": "One acronym: What Windows-style mitigation name also prevents data pages from executing?",
                "aliases": ["nx"],
                "explanation": "DEP, like NX, marks data memory as non-executable so injected bytes cannot run as code.",
                "hint": "Data Execution Prevention.",
                "relevance": "DEP/NX is a core mitigation against classic shellcode execution.",
            },
            {
                "term": "fgets",
                "question": "One word: Which C function can read input with a size limit for safer buffers?",
                "aliases": [],
                "explanation": "fgets accepts a maximum length, unlike unsafe unbounded input routines.",
                "hint": "It starts with f and gets a string.",
                "relevance": "Safer input handling lowers the risk of overflowing fixed-size buffers.",
            },
        ],
        "attack": [
            {
                "term": "netcat",
                "question": "One word: Which tool commonly connects to raw TCP challenge services?",
                "aliases": ["nc"],
                "explanation": "netcat opens raw network connections and is commonly used in beginner pwn challenges.",
                "hint": "It is often shortened to nc.",
                "relevance": "Many pwn exercises start by connecting to a service and observing its prompts.",
            },
            {
                "term": "recvuntil",
                "question": "One word: Which pwntools method waits until a chosen marker appears?",
                "aliases": [],
                "explanation": "recvuntil reads data until a delimiter appears, helping exploit scripts stay synchronized.",
                "hint": "It receives until a marker.",
                "relevance": "Reliable exploit scripts often wait for prompts before sending the next payload.",
            },
            {
                "term": "p64",
                "question": "One helper: Which pwntools function packs a 64-bit value for a payload?",
                "aliases": [],
                "explanation": "p64 packs integers into 64-bit little-endian bytes for 64-bit exploit payloads.",
                "hint": "The name includes 64.",
                "relevance": "Packing addresses correctly is essential in many binary exploitation exercises.",
            },
            {
                "term": "payload",
                "question": "One word: What exploit input is sent to trigger a control-flow change?",
                "aliases": [],
                "explanation": "A payload is the crafted data an exploit sends to reach the desired effect.",
                "hint": "It is the crafted exploit data.",
                "relevance": "Understanding payloads helps explain how binary exploitation works.",
            },
            {
                "term": "shellcode",
                "question": "One word: What are injected machine-code bytes commonly called?",
                "aliases": [],
                "explanation": "Shellcode is machine code used as part of an exploit payload.",
                "hint": "It often tries to spawn a shell.",
                "relevance": "Shellcode is a core term in pwn and exploit-development challenges.",
            },
            {
                "term": "ROP",
                "question": "One acronym: What technique chains existing instruction snippets ending in ret?",
                "aliases": [],
                "explanation": "ROP chains small existing code gadgets to perform actions without injecting new code.",
                "hint": "Return-oriented programming.",
                "relevance": "ROP explains how attackers may bypass non-executable memory protections.",
            },
            {
                "term": "overflow",
                "question": "One word: What bug happens when data writes past the end of a buffer?",
                "aliases": [],
                "explanation": "A buffer overflow writes outside the intended memory region and may corrupt nearby data.",
                "hint": "The buffer gets too full.",
                "relevance": "Buffer overflows are a foundational concept in pwn and memory-safety training.",
            },
            {
                "term": "format",
                "question": "One word: What string bug family abuses printf-style placeholders?",
                "aliases": ["printf"],
                "explanation": "Format-string bugs happen when user input is used as the printf format itself.",
                "hint": "Think printf placeholders.",
                "relevance": "Format-string vulnerabilities can leak memory and sometimes write memory.",
            },
        ],
    },
    "terminal_network": {
        "repair": [
            {
                "term": "firmware",
                "question": "One word: What embedded-device software do analysts inspect before restoring a controller?",
                "aliases": [],
                "explanation": "Firmware is software stored on a device that controls its low-level behavior.",
                "hint": "It runs on embedded devices.",
                "relevance": "Firmware review is important when restoring critical systems safely.",
            },
            {
                "term": "checksum",
                "question": "One word: What value can verify that firmware bytes have not changed?",
                "aliases": ["hash"],
                "explanation": "A checksum summarizes data so analysts can detect accidental or malicious changes.",
                "hint": "It checks integrity.",
                "relevance": "Integrity checks help defenders confirm trusted firmware before redeployment.",
            },
            {
                "term": "strings",
                "question": "One word: What readable byte sequences do analysts extract from a binary first?",
                "aliases": [],
                "explanation": "Strings can reveal messages, URLs, commands, or passwords embedded in a binary.",
                "hint": "It is also the name of a common reversing tool.",
                "relevance": "String extraction is a fast first step in malware and firmware triage.",
            },
        ],
        "attack": [
            {
                "term": "patch",
                "question": "One word: What operation changes binary bytes to alter program behavior?",
                "aliases": ["patching"],
                "explanation": "Patching modifies a binary, often to change checks, branches, or constants.",
                "hint": "Reverse engineers may do this to bypass a check.",
                "relevance": "Binary patching demonstrates how small code changes can affect system behavior.",
            },
            {
                "term": "XOR",
                "question": "One acronym: What reversible operation often hides constants in beginner reversing challenges?",
                "aliases": [],
                "explanation": "XOR can hide data and then reveal it again by applying the same key.",
                "hint": "It is written with the ^ operator in C and Python.",
                "relevance": "XOR is common in simple obfuscation and reverse-engineering puzzles.",
            },
            {
                "term": "debugging",
                "question": "One word: What means stepping through code while it runs?",
                "aliases": ["debug"],
                "explanation": "Debugging lets analysts inspect program state while instructions execute.",
                "hint": "A debugger is used for it.",
                "relevance": "Debugging is a practical way to understand suspicious or unknown binaries.",
            },
        ],
    },
}

def relevance_for(challenge_role, category):
    if challenge_role == "Python Engineer":
        return "Programming fluency helps defenders inspect automation, logs, and repair scripts during real incidents."
    if challenge_role == "Cryptographer":
        return "Pwn fundamentals help teams understand how network services fail and how mitigations stop binary exploitation."
    if challenge_role == "Network Analyst":
        return "Reverse-engineering logic helps analysts understand suspicious binaries and recover trusted system behavior."
    return "This skill supports practical cybersecurity investigation and system recovery."


def lesson_from_explanation(explanation):
    text = str(explanation or "").strip()
    if not text:
        return "Remember the core concept and apply it during the next lab action."
    first_sentence = text.split(". ", 1)[0].strip()
    if not first_sentence.endswith((".", "!", "?")):
        first_sentence += "."
    return first_sentence[:180]


def get_challenge(terminal_id, difficulty):
    challenge = CHALLENGES[terminal_id]
    details = challenge["difficulties"][difficulty]
    return {
        "id": details["id"],
        "role": challenge["role"],
        "title": details["title"],
        "category": details["category"],
        "difficulty": details["difficulty"],
        "question": details["prompt"],
        "prompt": details["prompt"],
        "options": details["options"],
        "answers": details["answers"],
        "answer": details["answers"][0],
        "explanation": details["explanation"],
        "lesson": lesson_from_explanation(details["explanation"]),
        "relevance": relevance_for(challenge["role"], details["category"]),
        "hint": details["hint"],
    }


def shuffled_options(correct, distractors):
    options = [str(correct)] + [str(value) for value in distractors if str(value) != str(correct)]
    options = options[:4]
    random.shuffle(options)
    answer_index = options.index(str(correct))
    answer_letter = chr(ord("a") + answer_index)
    return options, [str(correct), answer_letter, str(answer_index + 1)]


def generated_terminology_challenge(terminal_id, action):
    item = random.choice(TERMINOLOGY_CHALLENGES[terminal_id][action])
    answers = [item["term"], *item.get("aliases", [])]
    return {
        "title": f"Terminology: {item['term']}",
        "question": item["question"],
        "options": [],
        "answers": answers,
        "answer": item["term"],
        "explanation": item["explanation"],
        "lesson": lesson_from_explanation(item["explanation"]),
        "hint": item["hint"],
        "concept": f"terminology:{item['term'].casefold()}",
        "relevance": item["relevance"],
    }


def generated_python_challenge(difficulty, action):
    if action == "attack":
        if difficulty == "easy":
            secret_name = random.choice(("API_KEY", "DB_PASSWORD", "TOKEN"))
            correct = f"printing {secret_name} to logs"
            options, answers = shuffled_options(
                correct,
                ["using len(events)", "opening a file with with", "checking if a list is empty"],
            )
            return {
                "title": "Python Secret Leak",
                "question": f"Which Python mistake could help an attacker steal a Data Center {secret_name}?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": f"Secrets such as {secret_name} should not be printed or logged because logs are often widely accessible.",
                "hint": "Look for the option that exposes sensitive data.",
                "concept": "secret handling",
            }
        if difficulty == "medium":
            correct = "eval(user_input)"
            options, answers = shuffled_options(
                correct,
                ["int(user_input)", "len(user_input)", "user_input.strip()"],
            )
            return {
                "title": "Unsafe Eval",
                "question": "Which Python pattern can let attacker-controlled input run code in a Data Center script?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "eval() executes text as Python code, so attacker-controlled input can become command execution.",
                "hint": "One option executes text as code.",
                "concept": "unsafe eval",
            }
        correct = "pickle.loads(untrusted_bytes)"
        options, answers = shuffled_options(
            correct,
            ["json.loads(api_response)", "base64.b64decode(blob)", "hashlib.sha256(data).hexdigest()"],
        )
        return {
            "title": "Unsafe Deserialization",
            "question": "Which Python call is dangerous when the Data Center receives bytes from an untrusted user?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "pickle can execute code during deserialization, so untrusted pickle data is a serious risk.",
            "hint": "Pick the deserializer known for executing Python objects.",
            "concept": "unsafe deserialization",
        }

    if difficulty == "easy":
        count = random.randint(3, 7)
        values = [random.choice(("log", "auth", "dns", "api", "cache", "db")) for _ in range(count)]
        correct = count
        options, answers = shuffled_options(correct, [count - 1, count + 1, max(1, count - 2)])
        return {
            "title": "List Length Check",
            "question": f"Data Center logs are stored as {values!r}. What does len(logs) return?",
            "options": options,
            "answers": answers,
            "answer": str(correct),
            "explanation": f"len() counts the list items, so this list has {correct} entries.",
            "hint": "Count each comma-separated item inside the list.",
            "concept": "list length",
        }
    if difficulty == "medium":
        values = [random.randint(1, 5) for _ in range(3)]
        correct = sum(values)
        options, answers = shuffled_options(correct, [correct - 1, correct + 2, int("".join(str(v) for v in values))])
        return {
            "title": "Loop Sum Trace",
            "question": f"A repair script runs: total=0; for n in {values}: total += n; print(total). What prints?",
            "options": options,
            "answers": answers,
            "answer": str(correct),
            "explanation": f"The loop adds {' + '.join(str(v) for v in values)}, producing {correct}.",
            "hint": "Track total after each loop iteration.",
            "concept": "loop accumulation",
        }
    x = random.randint(2, 8)
    offset = random.randint(2, 6)
    correct = x * (x + offset)
    options, answers = shuffled_options(correct, [x + offset, correct + x, correct - offset])
    return {
        "title": "Repair Function Trace",
        "question": f"What is returned by f({x}) if def f(x): return (lambda y: y*x)(x+{offset})?",
        "options": options,
        "answers": answers,
        "answer": str(correct),
        "explanation": f"x is {x}, y becomes {x + offset}, and {x + offset} * {x} is {correct}.",
        "hint": "Substitute x first, then evaluate the lambda call.",
        "concept": "function tracing",
    }


def generated_crypto_challenge(difficulty, action):
    if action == "attack":
        choices = []
        if difficulty == "easy":
            host = random.choice(("core.lab", "10.0.0.5", "service.local"))
            port = random.choice(("31337", "4444", "9001"))
            correct = f"nc {host} {port}"
            options, answers = shuffled_options(correct, [f"ssh {host} {port}", f"ping {host}:{port}", f"curl {port} {host}"])
            choices.append({
                "title": "Service Connect",
                "question": f"Which command connects to the Network Core challenge service at {host} port {port}?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "netcat is commonly used to connect to raw TCP services during pwn challenges.",
                "hint": "The short command is often called nc.",
                "concept": "netcat",
            })
            correct = "writing 80 bytes into a 32-byte buffer"
            options, answers = shuffled_options(correct, ["closing a socket", "checking a username", "printing a banner"])
            choices.append({
                "title": "Overflow Trigger",
                "question": "Which input pattern best describes a buffer overflow attempt against the Network Core?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "A buffer overflow sends more data than a fixed buffer can safely hold.",
                "hint": "Look for data that exceeds the buffer size.",
                "concept": "buffer overflow",
            })
            correct = "printf(user_input)"
            options, answers = shuffled_options(correct, ["printf(\"%s\", user_input)", "fgets(buf, sizeof(buf), stdin)", "puts(\"ready\")"])
            choices.append({
                "title": "Format String Bug",
                "question": "Which C pattern can create a format-string vulnerability if user_input contains %x or %s?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "Using user input as the format string lets attackers control printf-style placeholders.",
                "hint": "The unsafe option uses user input as the format itself.",
                "concept": "format string",
            })
            return random.choice(choices)
        if difficulty == "medium":
            correct = "recvuntil(b'> ')"
            options, answers = shuffled_options(correct, ["sendline(b'id')", "p64(0x401000)", "process('./svc')"])
            choices.append({
                "title": "Pwntools Sync",
                "question": "In pwntools, which call waits for a Network Core service prompt before sending a payload?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "recvuntil() reads from the target until the chosen marker appears, keeping exploit scripts synchronized.",
                "hint": "Look for the receive method.",
                "concept": "pwntools receive",
            })
            value = random.choice(("0x401050", "0xdeadbeef", "0x41414141"))
            correct = f"p64({value})"
            options, answers = shuffled_options(correct, [f"p32({value})", f"u64({value})", f"recvuntil({value})"])
            choices.append({
                "title": "Payload Packing",
                "question": f"Which pwntools helper packs {value} as a 64-bit little-endian value for a payload?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "p64() packs integers into 64-bit little-endian bytes, a common step in 64-bit exploit payloads.",
                "hint": "The helper name includes the target bit width.",
                "concept": "payload packing",
            })
            correct = "%x %x %x"
            options, answers = shuffled_options(correct, ["AAAA", "exit", "help"])
            choices.append({
                "title": "Format Leak Probe",
                "question": "If a Network Core service unsafely calls printf(user_input), which input may leak stack values?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "Format placeholders such as %x can cause printf to read and print stack data.",
                "hint": "Choose the input made of printf placeholders.",
                "concept": "format string",
            })
            return random.choice(choices)
        value = random.choice(("0x401050", "0x400890", "0x7ffff7dd18b0"))
        correct = "chain existing code gadgets"
        options, answers = shuffled_options(correct, ["inject Python source", "rename the binary", "open a second terminal"])
        choices.append({
            "title": "ROP Strategy",
            "question": "What does a ROP attack do when NX blocks injected shellcode?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "Return-oriented programming chains existing instruction snippets, often ending in ret.",
            "hint": "ROP reuses code already in memory.",
            "concept": "rop",
        })
        correct = "leak an address"
        options, answers = shuffled_options(correct, ["disable logging", "increase timeout", "change the hostname"])
        choices.append({
            "title": "ASLR Bypass Idea",
            "question": "What information helps an exploit calculate useful addresses when ASLR is enabled?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "An address leak can reveal where code or libraries landed despite ASLR.",
            "hint": "ASLR randomizes addresses, so attackers want one revealed.",
            "concept": "aslr bypass",
        })
        correct = f"p64({value})"
        options, answers = shuffled_options(correct, [f"p32({value})", f"u64({value})", f"recvuntil({value})"])
        choices.append({
            "title": "64-bit Address Packing",
            "question": f"Which pwntools helper packs address {value} into a 64-bit payload slot?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "p64() packs a 64-bit value into the byte order expected by typical 64-bit Linux targets.",
            "hint": "The helper name includes 64.",
            "concept": "payload packing",
        })
        return random.choice(choices)

    choices = []
    if difficulty == "easy":
        correct = "check the input length before copying"
        options, answers = shuffled_options(correct, ["copy until the program crashes", "disable compiler warnings", "print the input twice"])
        choices.append({
            "title": "Bounds Check",
            "question": "Which defensive step helps prevent a Network Core buffer overflow?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "Checking length before copying keeps data within the destination buffer's bounds.",
            "hint": "Pick the option that checks size before copy.",
            "concept": "bounds checks",
        })
        correct = "fgets(buf, sizeof(buf), stdin)"
        options, answers = shuffled_options(correct, ["gets(buf)", "strcpy(buf, input)", "scanf(\"%s\", buf)"])
        choices.append({
            "title": "Safe Input Handling",
            "question": "Which C input pattern is safest for reading into a fixed Network Core buffer?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "fgets with sizeof(buf) limits how much input is copied into the buffer.",
            "hint": "Choose the option with an explicit size limit.",
            "concept": "safe input handling",
        })
        correct = "buffer overflow"
        options, answers = shuffled_options(correct, ["race condition", "phishing email", "weak password"])
        choices.append({
            "title": "Bug Identification",
            "question": "What vulnerability happens when input writes past a fixed-size buffer?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "A buffer overflow corrupts memory outside the intended buffer.",
            "hint": "The buffer receives too much data.",
            "concept": "buffer overflow",
        })
        return random.choice(choices)
    if difficulty == "medium":
        correct = "stack canary"
        options, answers = shuffled_options(correct, ["hard-coded password", "debug print", "larger banner"])
        choices.append({
            "title": "Canary Check",
            "question": "Which mitigation helps detect stack buffer overflows in a Network Core binary?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "A stack canary is checked before return; if an overflow changes it, the program aborts.",
            "hint": "It guards the stack near return data.",
            "concept": "stack canary",
        })
        correct = "ASLR"
        options, answers = shuffled_options(correct, ["ASCII", "HTTP", "SMTP"])
        choices.append({
            "title": "Address Randomization",
            "question": "Which mitigation randomizes where code and libraries load in memory?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "ASLR randomizes memory layout so hard-coded exploit addresses become unreliable.",
            "hint": "Address Space Layout Randomization.",
            "concept": "aslr",
        })
        correct = "NX / DEP"
        options, answers = shuffled_options(correct, ["larger stack", "debug symbols", "longer hostname"])
        choices.append({
            "title": "Executable Memory Policy",
            "question": "Which mitigation stops injected stack data from running as instructions?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "NX or DEP marks data memory as non-executable, blocking many shellcode attacks.",
            "hint": "It makes data memory non-executable.",
            "concept": "nx dep",
        })
        return random.choice(choices)
    correct = "printf(\"%s\", user_input)"
    options, answers = shuffled_options(correct, ["printf(user_input)", "printf(argv[1])", "syslog(user_input)"])
    choices.append({
        "title": "Format String Defense",
        "question": "Which pattern safely prints untrusted text without treating it as a printf format string?",
        "options": options,
        "answers": answers,
        "answer": correct,
        "explanation": "Using a fixed format string keeps user text as data instead of format instructions.",
        "hint": "The safe version uses %s as the fixed format.",
        "concept": "format string defense",
    })
    correct = "ASLR"
    options, answers = shuffled_options(correct, ["netcat", "recvuntil", "printf"])
    choices.append({
        "title": "ROP Hardening",
        "question": "Which mitigation makes fixed ROP gadget addresses unreliable between runs?",
        "options": options,
        "answers": answers,
        "answer": correct,
        "explanation": "ASLR changes load addresses, so attackers cannot rely on one fixed gadget location.",
        "hint": "It randomizes addresses.",
        "concept": "aslr",
    })
    correct = "bounds checks and safe input functions"
    options, answers = shuffled_options(correct, ["turn off NX", "remove canaries", "print raw user input"])
    choices.append({
        "title": "Overflow Prevention",
        "question": "What should defenders combine to reduce buffer-overflow risk in Network Core services?",
        "options": options,
        "answers": answers,
        "answer": correct,
        "explanation": "Bounds checks plus size-limited input functions prevent many writes past fixed buffers.",
        "hint": "Choose the option about limiting input size.",
        "concept": "bounds checks",
    })
    return random.choice(choices)


def generated_network_challenge(difficulty, action):
    if action == "attack":
        if difficulty == "easy":
            correct = "success"
            options, answers = shuffled_options(correct, ["crash", "network error", "infinite loop"])
            return {
                "title": "Return Value Trace",
                "question": "In decompiled Power Grid firmware, what does return 0 from main usually mean?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "A main() return value of 0 conventionally indicates successful execution.",
                "hint": "Think of process exit codes.",
                "concept": "return value",
            }
        if difficulty == "medium":
            password = random.choice(("open", "restore", "grid"))
            correct = password
            options, answers = shuffled_options(correct, ["admin", "0", "strcmp"])
            return {
                "title": "String Check Bypass",
                "question": f"A firmware check says strcmp(input, \"{password}\") == 0. Which input passes?",
                "options": options,
                "answers": answers,
                "answer": correct,
                "explanation": "strcmp returns 0 when both strings are equal, so the exact expected string passes.",
                "hint": "In C, strcmp equality is represented by zero.",
                "concept": "strcmp",
            }
        key = random.randint(0x20, 0x5F)
        mask = random.choice((0x13, 0x2A, 0x37))
        target = key ^ mask
        correct = f"0x{key:02x}"
        options, answers = shuffled_options(correct, [f"0x{target:02x}", f"0x{mask:02x}", f"0x{key + mask:02x}"])
        return {
            "title": "XOR Gate",
            "question": f"Power Grid firmware checks (x ^ {mask:#04x}) == {target:#04x}. Which x passes?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": f"XOR both sides by {mask:#04x}; {target:#04x} ^ {mask:#04x} is {correct}.",
            "hint": "XOR the target by the same mask.",
            "concept": "xor branch",
        }

    if difficulty == "easy":
        correct = "compare the known-good firmware hash"
        options, answers = shuffled_options(correct, ["increase screen brightness", "rename the binary", "disable all logs"])
        return {
            "title": "Firmware Integrity",
            "question": "What is the best first check before restoring Power Grid firmware?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "Comparing a cryptographic hash against a known-good value helps confirm the firmware has not been altered.",
            "hint": "Use an integrity check, not a cosmetic change.",
            "concept": "firmware integrity",
        }
    if difficulty == "medium":
        correct = "follow the branch that writes to relay_state"
        options, answers = shuffled_options(correct, ["ignore all branch labels", "delete the symbol table", "sort strings alphabetically"])
        return {
            "title": "Control Flow Triage",
            "question": "When reversing Power Grid firmware, which path is most relevant to safe restoration?",
            "options": options,
            "answers": answers,
            "answer": correct,
            "explanation": "Branches that modify relay or actuator state are safety-critical and should be reviewed first.",
            "hint": "Look for code that changes physical control state.",
            "concept": "control flow",
        }
    correct = "identify writes to memory-mapped I/O registers"
    options, answers = shuffled_options(correct, ["change the file icon", "count comment lines", "remove all function names"])
    return {
        "title": "Hardware Register Review",
        "question": "Which reverse-engineering step best finds firmware code that controls Power Grid hardware?",
        "options": options,
        "answers": answers,
        "answer": correct,
        "explanation": "Memory-mapped I/O register writes often control hardware devices, so they are important in firmware analysis.",
        "hint": "Hardware control often appears as special memory writes.",
        "concept": "memory-mapped io",
    }


def mission_question(system_name, action, question):
    if action == "attack":
        intros = (
            f"{system_name} attack simulation:",
            f"{system_name} intrusion drill:",
            f"{system_name} red-team prompt:",
        )
    else:
        intros = (
            f"{system_name} recovery ticket:",
            f"{system_name} defense check:",
            f"{system_name} restoration task:",
        )
    return f"{random.choice(intros)} {question}"


def make_local_challenge(terminal_id, difficulty, profile=None, action="repair", force_terminology=False):
    generators = {
        "terminal_python": generated_python_challenge,
        "terminal_crypto": generated_crypto_challenge,
        "terminal_network": generated_network_challenge,
    }
    topic = TERMINAL_TOPICS[terminal_id]
    if force_terminology or random.random() < TERMINOLOGY_CHANCE:
        details = generated_terminology_challenge(terminal_id, action)
    else:
        details = generators[terminal_id](difficulty, action)
    side = "Attack" if action == "attack" else "Defense"
    question = mission_question(topic["system"], action, details["question"])
    return {
        "id": f"local_{terminal_id}_{action}_{difficulty}_{random.randint(1000, 9999)}",
        "role": topic["role"],
        "title": f"{side}: {details['title']}",
        "category": topic["category"],
        "difficulty": difficulty,
        "question": question,
        "prompt": question,
        "options": details["options"],
        "answers": details["answers"],
        "answer": details["answer"],
        "explanation": details["explanation"],
        "lesson": details.get("lesson") or lesson_from_explanation(details["explanation"]),
        "relevance": details.get("relevance") or relevance_for(topic["role"], topic["category"]),
        "hint": details["hint"],
        "concept": details["concept"],
        "source": "local",
    }


def answer_matches(challenge, answer):
    normalized = str(answer).strip().casefold()
    return normalized in {str(value).strip().casefold() for value in challenge["answers"]}
