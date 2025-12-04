import json
from typing import Dict, List
from .dynamic_resource_fetcher import DynamicResourceFetcher

class RoadmapGenerator:
    """Generate detailed, personalized learning roadmaps with complete resources"""
    
    # High-quality resource databases
    YOUTUBE_CHANNELS = {
        'python': [
            {'channel': 'Corey Schafer', 'quality': 'excellent'},
            {'channel': 'Programming with Mosh', 'quality': 'excellent'},
            {'channel': 'Tech With Tim', 'quality': 'excellent'},
            {'channel': 'Code With Harry', 'quality': 'excellent'},
            {'channel': 'CS Dojo', 'quality': 'excellent'},
            {'channel': 'freeCodeCamp', 'quality': 'excellent'},
            {'channel': 'Kunal Kushwaha', 'quality': 'excellent'},
        ],
        'javascript': [
            {'channel': 'Traversy Media', 'quality': 'excellent'},
            {'channel': 'The Net Ninja', 'quality': 'excellent'},
            {'channel': 'freeCodeCamp', 'quality': 'excellent'},
            {'channel': 'JavaScript Mastery', 'quality': 'excellent'},
            {'channel': 'Coding Train', 'quality': 'excellent'},
        ],
        'web-development': [
            {'channel': 'Traversy Media', 'quality': 'excellent'},
            {'channel': 'The Net Ninja', 'quality': 'excellent'},
            {'channel': 'Kevin Powell', 'quality': 'excellent'},
            {'channel': 'freeCodeCamp', 'quality': 'excellent'},
        ],
        'django': [
            {'channel': 'Corey Schafer', 'quality': 'excellent'},
            {'channel': 'Programming with Mosh', 'quality': 'excellent'},
            {'channel': 'Code With Harry', 'quality': 'excellent'},
            {'channel': 'freeCodeCamp', 'quality': 'excellent'},
        ],
        'react': [
            {'channel': 'Traversy Media', 'quality': 'excellent'},
            {'channel': 'The Net Ninja', 'quality': 'excellent'},
            {'channel': 'JavaScript Mastery', 'quality': 'excellent'},
            {'channel': 'freeCodeCamp', 'quality': 'excellent'},
        ],
    }
    
    ROADMAPS = {
        'Advanced JavaScript & Node.js': {
            'modules': [
                {
                    'module_number': 1,
                    'name': 'JavaScript Fundamentals & Advanced Concepts',
                    'description': 'Master JavaScript core concepts from basics to advanced patterns',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': 'JavaScript Fundamentals',
                            'explanation': 'JavaScript is a versatile, event-driven programming language that powers interactive web applications. Understanding its core concepts is essential for modern web development.',
                            'duration_hours': 6,
                            'youtube_videos': [
                                {
                                    'title': 'JavaScript Fundamentals - Complete Course',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=hdI2bqOjy3c',
                                    'why': 'Comprehensive coverage of JS basics with practical examples'
                                },
                                {
                                    'title': 'The Complete JavaScript Course 2024',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=hKB1sLHwWME',
                                    'why': 'Updated curriculum covering modern JavaScript practices'
                                },
                                {
                                    'title': 'JavaScript Tutorial for Beginners',
                                    'channel': 'Programming with Mosh',
                                    'url': 'https://www.youtube.com/watch?v=W6NZfCO5tTE',
                                    'why': 'Clear explanations with live coding demonstrations'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'MDN Web Docs - JavaScript Guide',
                                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'JavaScript.info - Language Fundamentals',
                                    'url': 'https://javascript.info/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'FreeCodeCamp - JavaScript Handbook',
                                    'url': 'https://www.freecodecamp.org/news/the-complete-javascript-handbook-f26b2c71719c/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
                            'tools': [
                                {'name': 'Node.js', 'url': 'https://nodejs.org/', 'purpose': 'JavaScript runtime'},
                                {'name': 'Visual Studio Code', 'url': 'https://code.visualstudio.com/', 'purpose': 'Code editor'},
                                {'name': 'Chrome DevTools', 'url': 'https://developer.chrome.com/docs/devtools/', 'purpose': 'Debugging'}
                            ],
                            'summary': 'JavaScript fundamentals include variables, data types, operators, control flow, functions, and object-oriented programming. Variables store data using var, let, or const. Data types include primitives (numbers, strings, booleans) and objects (arrays, objects, functions). Control flow uses if/else, loops, and switch statements. Functions are reusable blocks of code. OOP uses objects, classes, and prototypes.',
                            'assignments': [
                                'Create a calculator app with basic arithmetic operations',
                                'Build a to-do list with add, remove, and mark complete functions',
                                'Write a program that checks if a number is prime'
                            ]
                        },
                        {
                            'topic_number': 2,
                            'name': 'Asynchronous JavaScript & Promises',
                            'explanation': 'Async programming is crucial for handling operations like API calls, file reading, and timers without blocking the main thread. Master callbacks, promises, and async/await syntax.',
                            'duration_hours': 5,
                            'youtube_videos': [
                                {
                                    'title': 'JavaScript Asynchronous Programming',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=PoRJizFVubE',
                                    'why': 'Clear explanation of callbacks, promises, and async/await with real examples'
                                },
                                {
                                    'title': 'Async JavaScript Tutorial',
                                    'channel': 'The Net Ninja',
                                    'url': 'https://www.youtube.com/watch?v=ZcQyJ-gxke0',
                                    'why': 'Step-by-step breakdown of asynchronous patterns'
                                },
                                {
                                    'title': 'Promises in JavaScript',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=4M4Mn6Z9sDQ',
                                    'why': 'Detailed coverage of promise chains and error handling'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'MDN - JavaScript Promises',
                                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'JavaScript.info - Promises',
                                    'url': 'https://javascript.info/promise-basics',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'Async/Await Guide',
                                    'url': 'https://javascript.info/async-await',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise',
                            'tools': [
                                {'name': 'Postman', 'url': 'https://www.postman.com/', 'purpose': 'API testing'},
                                {'name': 'Thunder Client (VS Code)', 'url': 'https://www.thunderclient.io/', 'purpose': 'HTTP testing'},
                                {'name': 'Node.js', 'url': 'https://nodejs.org/', 'purpose': 'Runtime environment'}
                            ],
                            'summary': 'Asynchronous JavaScript handles operations that take time: callbacks are functions passed as arguments; promises provide better control with .then() and .catch(); async/await is syntactic sugar making async code look synchronous. Error handling uses try/catch blocks. Common use cases: API calls with fetch, setTimeout, database operations.',
                            'assignments': [
                                'Fetch data from a public API and display it on the page',
                                'Create a promise chain that performs 3 sequential operations',
                                'Build an async function that retries failed API calls 3 times'
                            ]
                        },
                        {
                            'topic_number': 3,
                            'name': 'ES6+ Features & Modern JavaScript',
                            'explanation': 'ES6 (2015) introduced major improvements: arrow functions, classes, destructuring, template literals, and modules. These features make code more concise and maintainable.',
                            'duration_hours': 4,
                            'youtube_videos': [
                                {
                                    'title': 'ES6 Features in JavaScript',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=nyhj57j7DKE',
                                    'why': 'Comprehensive overview of all major ES6+ features'
                                },
                                {
                                    'title': 'JavaScript ES6 - The Complete Guide',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=IQofiPqLJ_8',
                                    'why': 'Practical examples of arrow functions, destructuring, and spread operator'
                                },
                                {
                                    'title': 'Modern JavaScript Patterns',
                                    'channel': 'Kyle Simpson (You Dont Know JS)',
                                    'url': 'https://www.youtube.com/watch?v=D9DyoksPxFc',
                                    'why': 'Deep dive into modern JS patterns and best practices'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'MDN - ES6 Features',
                                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/class',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'JavaScript.info - Modern JavaScript',
                                    'url': 'https://javascript.info/class',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'FreeCodeCamp - ES6 Handbook',
                                    'url': 'https://www.freecodecamp.org/news/write-less-do-more-with-javascript-es6-5fd4a8405c0d/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://tc39.es/ecma262/',
                            'tools': [
                                {'name': 'Babel', 'url': 'https://babeljs.io/', 'purpose': 'JavaScript compiler'},
                                {'name': 'ESLint', 'url': 'https://eslint.org/', 'purpose': 'Code quality tool'},
                                {'name': 'Webpack', 'url': 'https://webpack.js.org/', 'purpose': 'Module bundler'}
                            ],
                            'summary': 'ES6+ key features: arrow functions use "=>" syntax and lexical this binding; classes provide syntactic sugar for prototypal inheritance; destructuring extracts values from objects/arrays; template literals allow string interpolation with backticks; spread operator (...) copies arrays/objects; const/let provide block scope; modules use import/export. These features improve readability and reduce boilerplate code.',
                            'assignments': [
                                'Refactor callback-based code to use arrow functions and destructuring',
                                'Create a ES6 class with methods and demonstrate inheritance',
                                'Write a module with multiple exports and use it in another file'
                            ]
                        }
                    ]
                },
                {
                    'module_number': 2,
                    'name': 'Node.js & Backend Development',
                    'description': 'Learn server-side JavaScript with Node.js, build scalable APIs, and manage packages',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': 'Node.js Fundamentals',
                            'explanation': 'Node.js is a JavaScript runtime built on Chrome\'s V8 engine. It enables server-side JavaScript execution, non-blocking I/O, and package management through npm.',
                            'duration_hours': 5,
                            'youtube_videos': [
                                {
                                    'title': 'Node.js Tutorial for Beginners',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=fBNz5xF-Kx4',
                                    'why': 'Comprehensive introduction to Node.js with practical examples'
                                },
                                {
                                    'title': 'Complete Node.js Course',
                                    'channel': 'Programming with Mosh',
                                    'url': 'https://www.youtube.com/watch?v=TlB_eWDSMt4',
                                    'why': 'In-depth coverage from basics to advanced concepts'
                                },
                                {
                                    'title': 'Node.js Full Course',
                                    'channel': 'freeCodeCamp',
                                    'url': 'https://www.youtube.com/watch?v=RLtyhwFtEQY',
                                    'why': 'Long-form tutorial covering all essential concepts'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'Node.js Official Documentation',
                                    'url': 'https://nodejs.org/docs/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'Node.js Guide',
                                    'url': 'https://nodejs.org/en/docs/guides/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'FreeCodeCamp - Node.js Handbook',
                                    'url': 'https://www.freecodecamp.org/news/the-nodejs-handbook/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://nodejs.org/docs/latest/api/',
                            'tools': [
                                {'name': 'Node.js', 'url': 'https://nodejs.org/', 'purpose': 'JavaScript runtime'},
                                {'name': 'npm', 'url': 'https://www.npmjs.com/', 'purpose': 'Package manager'},
                                {'name': 'Nodemon', 'url': 'https://nodemon.io/', 'purpose': 'Auto-reload during development'}
                            ],
                            'summary': 'Node.js is event-driven and uses non-blocking I/O for scalability. Key concepts: modules (require/import), npm packages, event emitters, streams, file system operations, and global objects (process, console, Buffer). The event loop handles async operations. CommonJS (require/module.exports) and ES Modules (import/export) are two module systems.',
                            'assignments': [
                                'Create a file read/write program using Node.js fs module',
                                'Build a command-line tool that takes arguments and processes them',
                                'Organize code into modules and practice require/import statements'
                            ]
                        },
                        {
                            'topic_number': 2,
                            'name': 'Express.js & API Development',
                            'explanation': 'Express is a minimal, flexible Node.js web framework for building REST APIs and server-side applications with routing, middleware, and request handling.',
                            'duration_hours': 7,
                            'youtube_videos': [
                                {
                                    'title': 'Express.js Tutorial',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=lY6icVzg9Js',
                                    'why': 'Complete guide to Express with practical API examples'
                                },
                                {
                                    'title': 'Building REST APIs with Express',
                                    'channel': 'The Net Ninja',
                                    'url': 'https://www.youtube.com/watch?v=0oXYLzuucwE',
                                    'why': 'Step-by-step REST API development with Express'
                                },
                                {
                                    'title': 'Express.js Full Course',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=SccSCuHhOw0',
                                    'why': 'Complete course covering routing, middleware, and best practices'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'Express.js Official Documentation',
                                    'url': 'https://expressjs.com/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'Express.js Guide',
                                    'url': 'https://expressjs.com/en/guide/routing.html',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'Building APIs with Express',
                                    'url': 'https://www.freecodecamp.org/news/how-to-build-a-rest-api-with-node-and-express/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://expressjs.com/en/api.html',
                            'tools': [
                                {'name': 'Express.js', 'url': 'https://expressjs.com/', 'purpose': 'Web framework'},
                                {'name': 'Postman', 'url': 'https://www.postman.com/', 'purpose': 'API testing'},
                                {'name': 'Morgan', 'url': 'https://github.com/expressjs/morgan', 'purpose': 'HTTP request logger'}
                            ],
                            'summary': 'Express provides routing (GET, POST, PUT, DELETE), middleware for request processing, error handling, template rendering, and static file serving. Key concepts: app.listen(), req/res objects, route parameters, query strings, request body parsing (using body-parser or express.json()). Middleware functions execute in order and can modify req/res or pass control to next middleware.',
                            'assignments': [
                                'Build a todo API with GET, POST, PUT, DELETE endpoints',
                                'Create custom middleware for logging and authentication',
                                'Implement error handling middleware for different status codes'
                            ]
                        }
                    ]
                },
                {
                    'module_number': 3,
                    'name': 'Databases & Data Management',
                    'description': 'Master working with databases, ORMs, and data persistence in Node.js applications',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': 'SQL & Relational Databases',
                            'explanation': 'SQL (Structured Query Language) is used to manage relational databases like PostgreSQL, MySQL, and SQLite. Learn CRUD operations, joins, and complex queries.',
                            'duration_hours': 6,
                            'youtube_videos': [
                                {
                                    'title': 'SQL Tutorial for Beginners',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=OhsnFbYh8_U',
                                    'why': 'Comprehensive SQL tutorial with practical examples'
                                },
                                {
                                    'title': 'PostgreSQL Tutorial',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=qw--NyIydOU',
                                    'why': 'In-depth PostgreSQL with advanced features'
                                },
                                {
                                    'title': 'SQL Basics',
                                    'channel': 'freeCodeCamp',
                                    'url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY',
                                    'why': 'Comprehensive SQL fundamentals course'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'PostgreSQL Official Documentation',
                                    'url': 'https://www.postgresql.org/docs/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'SQL Tutorial',
                                    'url': 'https://www.w3schools.com/sql/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'SQL Guide',
                                    'url': 'https://sqlzoo.net/',
                                    'type': 'interactive_tutorial'
                                }
                            ],
                            'official_docs': 'https://www.postgresql.org/docs/current/',
                            'tools': [
                                {'name': 'PostgreSQL', 'url': 'https://www.postgresql.org/', 'purpose': 'Database server'},
                                {'name': 'pgAdmin', 'url': 'https://www.pgadmin.org/', 'purpose': 'Database management'},
                                {'name': 'DBeaver', 'url': 'https://dbeaver.io/', 'purpose': 'Database tool'}
                            ],
                            'summary': 'SQL fundamentals: SELECT retrieves data, INSERT adds rows, UPDATE modifies data, DELETE removes rows, CREATE TABLE defines structure. JOINS combine multiple tables (INNER, LEFT, RIGHT, FULL). WHERE filters data, GROUP BY aggregates, ORDER BY sorts. Aggregate functions: COUNT, SUM, AVG, MAX, MIN. Indexes improve query performance.',
                            'assignments': [
                                'Design a database schema for a blog with users, posts, and comments',
                                'Write queries to retrieve related data from multiple tables',
                                'Optimize slow queries using indexes and query analysis'
                            ]
                        },
                        {
                            'topic_number': 2,
                            'name': 'MongoDB & NoSQL',
                            'explanation': 'MongoDB is a document database storing data as JSON-like documents. Learn CRUD operations, aggregation, and document validation.',
                            'duration_hours': 5,
                            'youtube_videos': [
                                {
                                    'title': 'MongoDB Tutorial',
                                    'channel': 'Traversy Media',
                                    'url': 'https://www.youtube.com/watch?v=ofme2o29ngU',
                                    'why': 'Complete MongoDB guide with practical examples'
                                },
                                {
                                    'title': 'MongoDB Full Course',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=exHVAUXe8n8',
                                    'why': 'In-depth MongoDB course with CRUD operations'
                                },
                                {
                                    'title': 'NoSQL Databases Explained',
                                    'channel': 'Programming with Mosh',
                                    'url': 'https://www.youtube.com/watch?v=0buKQHpJ9Jg',
                                    'why': 'NoSQL concepts and MongoDB comparison with SQL'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'MongoDB Official Documentation',
                                    'url': 'https://docs.mongodb.com/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'MongoDB University',
                                    'url': 'https://university.mongodb.com/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'MongoDB Guide',
                                    'url': 'https://www.mongodb.com/docs/manual/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://docs.mongodb.com/manual/',
                            'tools': [
                                {'name': 'MongoDB', 'url': 'https://www.mongodb.com/', 'purpose': 'Document database'},
                                {'name': 'MongoDB Compass', 'url': 'https://www.mongodb.com/products/compass', 'purpose': 'GUI tool'},
                                {'name': 'Mongoose', 'url': 'https://mongoosejs.com/', 'purpose': 'ODM for Node.js'}
                            ],
                            'summary': 'MongoDB stores flexible JSON documents in collections. CRUD operations: insertOne/insertMany, findOne/find, updateOne/updateMany, deleteOne/deleteMany. Aggregation pipeline processes data in stages. Indexes improve query speed. Schema validation ensures data consistency. Replication provides high availability.',
                            'assignments': [
                                'Create a MongoDB collection with nested documents for an e-commerce system',
                                'Write aggregation queries to analyze user behavior data',
                                'Implement validation rules to ensure data quality'
                            ]
                        }
                    ]
                }
            ]
        },
        'Python & Django Web Development': {
            'modules': [
                {
                    'module_number': 1,
                    'name': 'Python Fundamentals',
                    'description': 'Master Python syntax, data structures, and core concepts for web development',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': 'Python Basics & Syntax',
                            'explanation': 'Python is a beginner-friendly, high-level language with simple syntax. Learn variables, data types, operators, and control flow.',
                            'duration_hours': 5,
                            'youtube_videos': [
                                {
                                    'title': 'Python for Beginners',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=hEgO047GxaQ',
                                    'why': 'Clear explanation of Python basics with live coding'
                                },
                                {
                                    'title': 'Python Tutorial',
                                    'channel': 'Corey Schafer',
                                    'url': 'https://www.youtube.com/watch?v=YYXdXT2l-V0&list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU',
                                    'why': 'Comprehensive Python tutorial series'
                                },
                                {
                                    'title': 'Python Programming',
                                    'channel': 'Programming with Mosh',
                                    'url': 'https://www.youtube.com/watch?v=_uQrJ0TkSuc',
                                    'why': 'Beginner-friendly Python course with practical examples'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'Python Official Documentation',
                                    'url': 'https://docs.python.org/3/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'Real Python Tutorials',
                                    'url': 'https://realpython.com/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'W3Schools Python Tutorial',
                                    'url': 'https://www.w3schools.com/python/',
                                    'type': 'interactive_tutorial'
                                }
                            ],
                            'official_docs': 'https://docs.python.org/3/',
                            'tools': [
                                {'name': 'Python', 'url': 'https://www.python.org/', 'purpose': 'Programming language'},
                                {'name': 'PyCharm', 'url': 'https://www.jetbrains.com/pycharm/', 'purpose': 'IDE'},
                                {'name': 'Jupyter Notebook', 'url': 'https://jupyter.org/', 'purpose': 'Interactive coding'}
                            ],
                            'summary': 'Python fundamentals: variables store data, data types include int, float, string, bool, list, dict, tuple; operators perform arithmetic, comparison, logical operations; control flow uses if/elif/else and loops (for, while); functions are reusable code blocks with parameters and return values; scope determines variable access.',
                            'assignments': [
                                'Write a program that calculates compound interest',
                                'Build a number guessing game with loops and conditionals',
                                'Create a function that reverses a string and checks if it\'s a palindrome'
                            ]
                        }
                    ]
                },
                {
                    'module_number': 2,
                    'name': 'Django Framework',
                    'description': 'Learn to build scalable web applications with Django',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': 'Django Fundamentals',
                            'explanation': 'Django is a high-level Python framework that follows MTV pattern. Learn project structure, apps, models, views, templates, and URL routing.',
                            'duration_hours': 8,
                            'youtube_videos': [
                                {
                                    'title': 'Django for Beginners',
                                    'channel': 'Corey Schafer',
                                    'url': 'https://www.youtube.com/watch?v=UmljXQIjC0E&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p',
                                    'why': 'Comprehensive Django tutorial series covering all fundamentals'
                                },
                                {
                                    'title': 'Django REST Framework',
                                    'channel': 'Code With Harry',
                                    'url': 'https://www.youtube.com/watch?v=0boS3iCFVcM',
                                    'why': 'Build REST APIs with Django REST Framework'
                                },
                                {
                                    'title': 'Django Full Course',
                                    'channel': 'Programming with Mosh',
                                    'url': 'https://www.youtube.com/watch?v=rHux0gMZ3Eg',
                                    'why': 'Complete Django course with database and deployment'
                                }
                            ],
                            'documentation': [
                                {
                                    'title': 'Django Official Documentation',
                                    'url': 'https://docs.djangoproject.com/',
                                    'type': 'official_documentation'
                                },
                                {
                                    'title': 'Django for Beginners Book',
                                    'url': 'https://djangoforbeginners.com/',
                                    'type': 'comprehensive_guide'
                                },
                                {
                                    'title': 'Real Python Django Tutorials',
                                    'url': 'https://realpython.com/tutorials/django/',
                                    'type': 'tutorial'
                                }
                            ],
                            'official_docs': 'https://docs.djangoproject.com/en/stable/',
                            'tools': [
                                {'name': 'Django', 'url': 'https://www.djangoproject.com/', 'purpose': 'Web framework'},
                                {'name': 'Django REST Framework', 'url': 'https://www.django-rest-framework.org/', 'purpose': 'API development'},
                                {'name': 'PostgreSQL', 'url': 'https://www.postgresql.org/', 'purpose': 'Database'}
                            ],
                            'summary': 'Django MTV: Models define database structure, Views handle logic, Templates render HTML. Key components: URLconf for routing, ORM for database access, forms for user input, middleware for request processing. Django admin provides CRUD interface automatically. Static files serve CSS/JS. Migrations track database changes.',
                            'assignments': [
                                'Build a blog application with models for posts and comments',
                                'Create views for listing, creating, updating, and deleting posts',
                                'Implement user authentication with login and registration'
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    def __init__(self):
        self.skill_levels = {
            'beginner': {'weight': 1.0, 'skip_basics': False, 'extra_resources': True},
            'intermediate': {'weight': 0.7, 'skip_basics': True, 'extra_resources': False},
            'advanced': {'weight': 0.5, 'skip_basics': True, 'extra_resources': False},
            'slow learner': {'weight': 1.5, 'skip_basics': False, 'extra_resources': True},
            'fast learner': {'weight': 0.4, 'skip_basics': True, 'extra_resources': False},
        }
        # Initialize dynamic resource fetcher
        self.resource_fetcher = DynamicResourceFetcher()
    
    def generate_roadmap(self, course_name: str, user_skill_level: str, duration_weeks: int = 12) -> Dict:
        """Generate a comprehensive learning roadmap"""
        
        # Get base roadmap
        if course_name not in self.ROADMAPS:
            return self._get_fallback_roadmap(course_name, duration_weeks)
        
        roadmap_data = self.ROADMAPS[course_name]
        skill_config = self.skill_levels.get(user_skill_level.lower(), self.skill_levels['beginner'])
        
        # Process roadmap based on skill level
        processed_roadmap = self._process_roadmap_by_skill_level(
            roadmap_data,
            user_skill_level,
            duration_weeks,
            skill_config
        )
        
        return processed_roadmap
    
    def _process_roadmap_by_skill_level(self, roadmap, skill_level, duration_weeks, config):
        """Customize roadmap based on skill level and duration"""
        processed = {
            'course_name': roadmap.get('name', 'Course'),
            'skill_level': skill_level,
            'duration_weeks': duration_weeks,
            'modules': []
        }
        
        total_original_hours = sum(
            sum(topic['duration_hours'] for topic in module['topics'])
            for module in roadmap['modules']
        )
        
        # Calculate time multiplier
        time_multiplier = (duration_weeks * 8) / total_original_hours
        
        for module in roadmap['modules']:
            processed_module = {
                'module_number': module['module_number'],
                'name': module['name'],
                'description': module['description'],
                'topics': []
            }
            
            for topic in module['topics']:
                processed_topic = {
                    'topic_number': topic['topic_number'],
                    'name': topic['name'],
                    'explanation': topic['explanation'],
                    'duration_hours': round(topic['duration_hours'] * time_multiplier, 1),
                    'youtube_videos': topic['youtube_videos'][:3],
                    'documentation': topic['documentation'][:3],
                    'official_docs': topic['official_docs'],
                    'tools': topic['tools'][:4],
                    'summary': topic['summary'],
                    'assignments': topic['assignments'][:3]
                }
                
                processed_module['topics'].append(processed_topic)
            
            processed['modules'].append(processed_module)
        
        return processed
    
    def _get_fallback_roadmap(self, course_name: str, duration_weeks: int) -> Dict:
        """Fallback roadmap for unknown courses"""
        hours_per_topic = (duration_weeks * 8) / 5
        
        return {
            'course_name': course_name,
            'skill_level': 'beginner',
            'duration_weeks': duration_weeks,
            'modules': [
                {
                    'module_number': 1,
                    'name': f'Introduction to {course_name}',
                    'description': f'Master the fundamentals of {course_name}',
                    'topics': [
                        {
                            'topic_number': 1,
                            'name': f'Getting Started with {course_name}',
                            'explanation': f'Begin your journey with {course_name}. Learn core concepts, tools, and best practices.',
                            'duration_hours': hours_per_topic,
                            'youtube_videos': [
                                {
                                    'title': f'{course_name} Tutorial for Beginners',
                                    'channel': 'Traversy Media',
                                    'url': '#',
                                    'why': 'Comprehensive introduction'
                                },
                                {
                                    'title': f'Complete {course_name} Course',
                                    'channel': 'Code With Harry',
                                    'url': '#',
                                    'why': 'Practical examples and projects'
                                },
                                {
                                    'title': f'{course_name} Fundamentals',
                                    'channel': 'freeCodeCamp',
                                    'url': '#',
                                    'why': 'Complete course from basics'
                                }
                            ],
                            'documentation': [
                                {'title': f'{course_name} Official Docs', 'url': '#', 'type': 'official'},
                                {'title': f'{course_name} Guide', 'url': '#', 'type': 'guide'},
                                {'title': f'{course_name} Tutorial', 'url': '#', 'type': 'tutorial'}
                            ],
                            'official_docs': '#',
                            'tools': [{'name': course_name, 'url': '#', 'purpose': 'Primary tool'}],
                            'summary': f'Start with {course_name} fundamentals.',
                            'assignments': [
                                f'Create your first {course_name} project',
                                f'Complete basic {course_name} exercises',
                                f'Build a simple {course_name} application'
                            ]
                        }
                    ]
                }
            ]
        }
