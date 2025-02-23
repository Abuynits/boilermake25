code_file_extensions = [
    # Web Development
    '.html', '.htm', '.xhtml', '.css', '.scss', '.sass', '.less',
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.php', '.asp', '.aspx',
    '.jsp', '.cshtml', '.razor',
    
    # Python
    '.py', '.pyx', '.pxd', '.pxi', '.pyc', '.pyd', '.pyo',
    '.pyw', '.ipynb', '.rpy',
    
    # Java and JVM
    '.java', '.class', '.jar', '.war', '.ear', '.jsp',
    '.kt', '.kts', '.ktm',  # Kotlin
    '.groovy', '.gvy', '.gy', '.gsh',
    '.scala', '.sc',
    
    # C and C++
    '.c', '.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp',
    '.hh', '.hxx', '.h++', '.inc',
    
    # C#
    '.cs', '.csx', '.vb', '.fs', '.fsx',  # F#
    
    # Ruby
    '.rb', '.rbw', '.rake', '.gemspec', '.rbx',
    '.ru', '.erb', '.rhtml', '.rjs',
    
    # Go
    '.go', '.mod',
    
    # Rust
    '.rs', '.rlib',
    
    # Swift and Objective-C
    '.swift', '.m', '.mm',
    
    # Shell Scripting
    '.sh', '.bash', '.csh', '.tcsh', '.zsh', '.fish',
    '.bat', '.cmd', '.ps1', '.psm1',
    
    # Database
    '.sql', '.mysql', '.pgsql', '.plsql',
    
    # Configuration and Data
    '.xml', '.json', '.yaml', '.yml', '.toml', '.ini',
    '.conf', '.cfg', '.properties',
    
    # Mobile Development
    '.dart',  # Flutter/Dart
    '.kt',    # Android/Kotlin
    '.swift', # iOS/Swift
    
    # Other Languages
    '.lua', '.pl', '.pm',    # Perl
    '.r', '.rmd',           # R
    '.coffee',             # CoffeeScript
    '.elm',                # Elm
    '.ex', '.exs',         # Elixir
    '.erl', '.hrl',        # Erlang
    '.hs', '.lhs',         # Haskell
    '.lisp', '.cl', '.el',  # Lisp family
    '.clj', '.cljs',       # Clojure
    '.ml', '.mli',         # OCaml
    '.php', '.phtml',      # PHP
    '.rs',                 # Rust
    '.scala',              # Scala
    '.ts',                 # TypeScript
    
    # Assembly
    '.asm', '.s', '.nasm',
    
    # Documentation
    # '.md', '.rst', '.tex', '.adoc',
    
    # Build and Package
    '.cmake', '.make', '.mk', '.mak',
    '.gradle', '.pom', '.ant',
    
    # Shader Languages
    '.glsl', '.hlsl', '.shader', '.cg',
    
    # Hardware Description
    '.v', '.vh', '.vhd', '.vhdl',
    
    # Protocol Buffers and Schemas
    '.proto', '.thrift', '.avsc',
    
    # AI/ML
    # '.onnx', '.pkl', '.model',
    # '.pth',  # PyTorch
    # '.h5',   # Keras/TensorFlow
    
    # Container and Infrastructure
    # '.dockerfile', '.containerfile',
    # '.tf', '.tfvars',  # Terraform
    # '.yaml', '.yml',   # Kubernetes/Docker Compose
    
    # Template Languages
    '.jinja', '.j2', '.tmpl', '.tpl',
    '.mustache', '.handlebars', '.hbs',
    
    # IDL (Interface Description Language)
    # '.idl', '.odl', '.midl', '.pidl',
    
    # Game Development
    # '.gd',   # Godot
    # '.unity', # Unity
    # '.unitypackage',
    # '.blend',  # Blender Python
    
    # Legacy/Historical
    '.cob', '.cbl',  # COBOL
    '.ftn', '.f', '.f77', '.f90', '.f95',  # FORTRAN
    '.pas',  # Pascal
    '.ada',  # Ada
]

code_file_extensions = sorted(list(set(code_file_extensions)))