# AI Code Generation Indicators of Compromise (IOC)

## Code Structure & Patterns

### Excessive Documentation
**Indicators:**
- Every function has detailed JSDoc/docstrings even for trivial operations
- Comments explaining obvious code behavior
- Redundant inline comments for simple operations
- Documentation that restates what the code does rather than why

**Mitigation:**
- Remove obvious comments
- Focus documentation on business logic and complex algorithms only
- Use meaningful variable/function names to reduce need for comments
- Document WHY, not WHAT

**References:**
- [Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884)
- [Code Complete 2 by Steve McConnell - Chapter 32: Self-Documenting Code](https://www.microsoftpressstore.com/store/code-complete-9780735619678)
- [Google Style Guides: Comments](https://google.github.io/styleguide/cppguide.html#Comments)

### Generic Naming Patterns
**Indicators:**
- Variables named: result, data, temp, item, element, obj, resp, res
- Functions named: handleData, processItem, updateValue, getValue
- Classes named: DataHandler, ItemProcessor, BaseClass, HelperClass

**Mitigation:**
- Use domain-specific meaningful names (userProfileData vs data)
- Replace generic terms with business context
- Avoid overly descriptive names that sound AI-generated

**References:**
- [Clean Code: Meaningful Names Chapter](https://blog.cleancoder.com/uncle-bob/2017/05/03/TestDefinitions.html)
- [Naming Things in Code by Kevlin Henney](https://www.youtube.com/watch?v=5tg1ONG18H8)
- [The Art of Readable Code by Dustin Boswell](https://www.oreilly.com/library/view/the-art-of/9781449318482/)

## Error Handling & Validation

### Over-Engineering Simple Operations
**Indicators:**
- try-catch blocks for operations that rarely fail
- Extensive input validation for internal functions
- Multiple fallback mechanisms for simple operations
- Defensive programming taken to extremes

**Mitigation:**
- Remove unnecessary error handling
- Simplify validation to actual requirements
- Trust internal function calls more
- Focus error handling on external boundaries

**References:**
- [Release It! by Michael T. Nygard - Design Patterns for Stability](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Building Microservices by Sam Newman - Error Handling](https://www.oreilly.com/library/view/building-microservices/9781491950340/)
- [Clean Architecture by Robert C. Martin - Error Handling](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

### Generic Error Messages
**Indicators:**
- "An error occurred while processing"
- "Invalid input provided"
- "Operation failed successfully"
- Overly polite error messages

**Mitigation:**
- Use specific, actionable error messages
- Include context-specific information
- Use informal language occasionally
- Reference actual business requirements

**References:**
- [Don't Make Me Think by Steve Krug - Error Messages](https://www.amazon.com/Dont-Make-Think-Revisited-Usability/dp/0321965515)
- [Design of Everyday Things by Don Norman - Error Recovery](https://www.amazon.com/Design-Everyday-Things-Revised-Expanded/dp/0465050654)
- [Nielsen Norman Group: Error Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/)

### Perfect Naming Conventions
**Indicators:**
- No context-specific naming patterns

**Mitigation:**
- Use team-specific abbreviations
- Add context from business domain

**References:**
- [Naming Conventions in Programming by Peter Norvig](http://norvig.com/21-days.html)
- [Code Conventions for Java by Oracle](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html)
- [Naming Things: One of the Hardest Problems in Computer Science](https://www.karlton.org/2017/12/naming-things-hard/)

### Missing Context
**Indicators:**
- No business-specific requirements
- Generic implementation without domain context

**Mitigation:**
- Add references to team decisions
- Include business requirement comments
- Add domain-specific constraints

**References:**
- [The Cathedral and the Bazaar by Eric S. Raymond](https://www.amazon.com/Cathedral-Bazaar-Musings-Accidental-Revolutionary/dp/0596001088)
- [Peopleware by Tom DeMarco and Timothy Lister](https://www.amazon.com/Peopleware-Productive-Projects-Teams-3rd/dp/0321934113)
- [Team Geek by Brian W. Fitzpatrick](https://www.amazon.com/Team-Geek-Software-Developers-Working/dp/1449302440)

### Unusual characters
**Indicators:**
- Usage of emojis
- Usage of whitespaces not beeing a space
- Unsual characters or line breaks

**Mitigation:**
- Do not use emojis or other visual signs
- Only use space for code


