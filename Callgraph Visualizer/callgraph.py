import os
import re
import sys 
 
def find_source_files(path):
 
    files = []

    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    return files

def print_files_tree(path):
    path = os.path.abspath(path)
 
    print(os.path.basename(path))
 
    def print_tree(current_path, prefix=""):
        entries = sorted(os.listdir(current_path))

        for index, entry in enumerate(entries):
            full_path = os.path.join(current_path, entry)
            is_last = index == len(entries) - 1
 
            if is_last:
                branch = "└── "
            else:
                branch = "├── "
 
            if os.path.isdir(full_path):
                print(prefix + branch + entry )
 
                if is_last:
                    child_prefix = prefix + "    "
                else:
                    child_prefix = prefix + "│   "
 
                print_tree(full_path, child_prefix)
 
            else:
                print(prefix + branch + entry)
 
    print_tree(path)

def print_functions_tree(path):
    path = os.path.abspath(path)
 
    print(os.path.basename(path))
 
    def print_tree(current_path, prefix=""):
        entries = sorted(os.listdir(current_path))

        for index, entry in enumerate(entries):
            full_path = os.path.join(current_path, entry)
            is_last = index == len(entries) - 1
 
            if is_last:
                branch = "└── "
            else:
                branch = "├── "
 
            if os.path.isdir(full_path):
                print(prefix + branch + entry )
 
                if is_last:
                    child_prefix = prefix + "    "
                else:
                    child_prefix = prefix + "│   "
 
                print_tree(full_path, child_prefix)
 
            else:
                extension = os.path.splitext(entry)[1].lower()
 
                source_extensions = (".c", ".h", ".cpp",".hpp", ".cc", ".java" )
 
                if extension in source_extensions:
                    print(prefix + branch + entry)
 
                    functions = extract_functions(full_path)
 
                    if is_last:
                        function_prefix = prefix + "    "
                    else:
                        function_prefix = prefix + "│   "
 
                    for function, line_number in functions:
                        print(function_prefix + "└── " + function + "()")
 
    print_tree(path)
 
 
 
def extract_functions(filename):
    functions = []
 
    with open(filename, "r") as file:
        content = file.read()
 
    pattern = re.compile(
        r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*\{',re.MULTILINE
    )
 
    keywords = {
        "if",
        "else",
        "for",
        "while",
        "switch",
        "catch"
    }
 
    for match in pattern.finditer(content):
        function=match.group(1)

        if function not in keywords:
            line_number=content.count("\n",0,match.start())+1
            functions.append((function,line_number))
 
    return functions
 
 
def extract_calls(filename, defined_functions):
 
    calls = []
 
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        content = file.read()
 
    definition_pattern = re.compile(
        r'\b([A-Za-z_][A-Za-z0-9_]*)\s*'
        r'\([^;{}]*\)\s*\{',
        re.MULTILINE
    )
 
    call_pattern = re.compile(
        r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\('
    )
 
    keywords = {
        "if", "else", "for", "while",
        "switch", "catch", "sizeof"
    }
 
    definitions = list(
        definition_pattern.finditer(content)
    )
 
    for index, definition in enumerate(definitions):
 
        current_function = definition.group(1)
 
        start = definition.end()
 
        if index + 1 < len(definitions):
            end = definitions[index + 1].start()
        else:
            end = len(content)
 
        body = content[start:end]
 
        for match in call_pattern.finditer(body):
 
            called_function = match.group(1)
 
            if called_function in keywords:
                continue
 
            if called_function not in defined_functions:
                continue
 
            call_position = start + match.start()
 
            line_number = (
                content.count("\n", 0, call_position) + 1
            )
 
            calls.append(
                (
                    current_function,
                    called_function,
                    filename,
                    line_number
                )
            )
 
    return calls
 
 

def build_call_graph(calls):
    call_graph = {}
 
    for caller, called, filename, line in calls:
 
        if caller not in call_graph:
            call_graph[caller] = []
 
        call_graph[caller].append(called)
 
    return call_graph
 

 
 
def print_children(function, call_graph, prefix, visited):
 
    if function in visited:
        return
 
    visited.add(function)
 
    children = call_graph.get(function, [])
 
    for index, child in enumerate(children):
 
        is_last = index == len(children) - 1
 
        if is_last:
            branch = "└── "
            child_prefix = prefix + "    "
        else:
            branch = "├── "
            child_prefix = prefix + "│   "
 
        print(prefix + branch + child + "()")
 
        print_children(
            child,
            call_graph,
            child_prefix,
            visited.copy()
        )
 
 
 
 
 
def reverse_lookup(target, calls):
    print(target + "() called by:")
 
    found = False
 
    for caller, called, filename, line in calls:
 
        if called == target:
            print(
                "    " +
                caller +
                "() " +
                os.path.basename(filename) +
                ":" +
                str(line)
            )
 
            found = True
 
    if not found:
        print("    No callers found.")
 
 
  
def main():
    source_directory =os.getcwd()

    if len(sys.argv)>=2 and sys.argv[1]=="--files":
        print_files_tree(source_directory)
        return

    if len(sys.argv)>=2 and sys.argv[1]=="--functions":
        print_functions_tree(source_directory)
        return  

   
 
    files = find_source_files(source_directory)

    if not files:
        print("No source files found")
        return
 
    all_functions = set()
 
    for file in files:
 
        functions = extract_functions(file)
 
        for function, line in functions:
            all_functions.add(function)

    if not all_functions:
        print("No functions found")   
        return     
 
    all_calls = []
 
    for file in files:
 
        calls = extract_calls(file, all_functions)
 
        all_calls.extend(calls)
 
    if len(sys.argv) >= 3 and sys.argv[1] == "--calls":
 
        target = sys.argv[2]
 
        reverse_lookup(target, all_calls)
 
    else:
 
        call_graph = build_call_graph(all_calls)
 
        print("Call Tree:")
        print(os.path.basename(source_directory))
 
        children = call_graph.get("main", [])

 
        for index, child in enumerate(children):
            is_last = index == len(children) - 1
 
            if is_last:
                branch = "└── "
                child_prefix = "    "
            else:
                branch = "├── "
                child_prefix = "│   "
 
            print(branch + child + "()")
 
            print_children(
            child,
            call_graph,
            child_prefix,
            {"main"}
            )
 
 
 
if __name__ == "__main__":
    with open("output.txt","w",encoding="utf-8")as file:
        sys.stdout=file
        main()
 