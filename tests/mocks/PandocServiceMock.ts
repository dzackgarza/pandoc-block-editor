// Basic structure for a PandocService mock
// This will be expanded as needed when actual Pandoc interactions are developed.

// Basic structure for a PandocService mock
// This will be expanded as needed when actual Pandoc interactions are developed.

interface MockPandocBlock {
  type: string;
  text?: string;
  // Add other properties as needed for mock ASTs
}

interface PandocAst {
  type: string;
  content: MockPandocBlock[];
  // Add other top-level AST properties if necessary
}

export class PandocServiceMock {
  async parseToAst(markdown: string): Promise<PandocAst> {
    console.log(`PandocServiceMock: parseToAst called with markdown: ${markdown.substring(0, 50)}...`);
    if (markdown.includes('error_case')) {
      throw new Error('Simulated Pandoc parsing error');
    }
    return { type: 'doc', content: [{ type: 'paragraph', text: 'mocked AST' }] };
  }

  async convertAstToHtml(ast: PandocAst): Promise<string> {
    console.log(`PandocServiceMock: convertAstToHtml called with AST: ${JSON.stringify(ast)}`);
    if (ast.content && ast.content.length > 0 && ast.content[0].text === 'mocked AST') {
      return '<p>mocked AST</p>';
    }
    return '<p>Default mocked HTML</p>';
  }

  async convertMarkdownToHtml(markdown: string): Promise<string> {
    console.log(`PandocServiceMock: convertMarkdownToHtml called with markdown: ${markdown.substring(0,50)}...`);
    const ast = await this.parseToAst(markdown);
    return this.convertAstToHtml(ast);
  }
}

// Example usage (typically in a test file):
// import { PandocServiceMock } from './PandocServiceMock';
// const mockPandocService = new PandocServiceMock();
// const html = await mockPandocService.convertMarkdownToHtml('Some markdown');
// expect(html).toBe('<p>mocked AST</p>');
