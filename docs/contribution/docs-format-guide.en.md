# Documentation format guide

This page lists the some rules that should be followed when writing OpenTenBase documentation. Please read this page carefully before writing or modifying documentation to help you write higher quality content.

## Storage format and document links

1. **File names are written in lowercase letters, and words are separated by `-`.** For example: `docs-format-guide.md`.
2. **Add `.en` after the file name of an English documentation.** For example: `docs-format-guide.en.md`. Files for English documentations are stored in the same directory as Chinese documentations.
3. Use relative paths for internal links, for example: `[Format Guide](docs-format-guide.md)`, `[FAQ](../faq.md)`.
4. All the images used are stored in the `docs/assets` directory of the repository and have a meaningful file names. Use relative paths for image references, for example: `![OpenTenBase favicon](./assets/favicon.png)`.

## Basic format requirements for documents

- Level 1 headings in form of `#` or `<h1>` are not allowed in the document body except for the title of the document, which is the same as the title of the document and written in the first line of the document.
- A space is required after the number sign of headings. For example: `## Second-level heading`.
- A white line is required after a heading.
- Use 4 spaces for indentation, not Tab.
- For block-level elements such as code blocks, tables, etc., there should be a blank line before and after the element.
- An indentation of 4 spaces is required for second-level lists.
- The content added to the same level list should have an indentation of 4 spaces, and two blank lines should be added before and after the content.
- For admonitions using the `???` or `!!!` syntax, an identation of 4 spaces is required for each line of text, even if it is a blank line. An empty line is required before and after the admonitions, but not before and after the content.
- Code blocks used in form of ```` ``` ```` should have a language specified. For example: ```` ``` shell ````. If the code content is plain text, specify `text` as the language.

