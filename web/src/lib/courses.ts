export type Course = {
  slug: string;
  title: string;
  level: "Beginner" | "Intermediate" | "Advanced";
  hours: number;
  tag: string;
  desc: string;
  xp: number;
};

export const COURSES: Course[] = [
  { slug: "learn-python-3", title: "Learn Python 3", level: "Beginner", hours: 25, tag: "Python", xp: 250, desc: "Master the fundamentals of Python — variables, loops, functions, and OOP." },
  { slug: "learn-javascript", title: "Learn JavaScript", level: "Beginner", hours: 20, tag: "JavaScript", xp: 200, desc: "The language of the web. From syntax to async patterns." },
  { slug: "learn-react", title: "Learn React", level: "Intermediate", hours: 18, tag: "Web Dev", xp: 360, desc: "Build modern UIs with components, hooks, and state management." },
  { slug: "data-science-foundations", title: "Data Science Foundations", level: "Beginner", hours: 30, tag: "Data", xp: 300, desc: "Numpy, Pandas, statistics and the data analysis workflow." },
  { slug: "ml-with-pytorch", title: "ML with PyTorch", level: "Advanced", hours: 40, tag: "AI", xp: 800, desc: "Build and train neural networks end-to-end with PyTorch." },
  { slug: "sql-essentials", title: "SQL Essentials", level: "Beginner", hours: 12, tag: "Data", xp: 120, desc: "Query relational databases with confidence." },
  { slug: "node-apis", title: "Build APIs with Node.js", level: "Intermediate", hours: 22, tag: "Backend", xp: 440, desc: "Design and ship RESTful APIs with Express." },
  { slug: "intro-cybersecurity", title: "Intro to Cybersecurity", level: "Beginner", hours: 15, tag: "Security", xp: 150, desc: "Threat models, networks, and ethical hacking basics." },
  { slug: "typescript-deep-dive", title: "TypeScript Deep Dive", level: "Intermediate", hours: 16, tag: "Web Dev", xp: 320, desc: "Generics, conditional types, and advanced patterns." },
  { slug: "swift-ios", title: "iOS with Swift", level: "Intermediate", hours: 28, tag: "Mobile", xp: 560, desc: "Ship native iOS apps with SwiftUI." },
  { slug: "go-microservices", title: "Go Microservices", level: "Advanced", hours: 30, tag: "Backend", xp: 600, desc: "Concurrency, gRPC, and production-grade Go services." },
  { slug: "design-systems", title: "Design Systems 101", level: "Beginner", hours: 10, tag: "Design", xp: 100, desc: "Tokens, components and scaling visual languages." },
];
