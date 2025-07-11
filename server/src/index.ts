#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
  name: "roo-mcp-server",
  version: "0.1.0"
});

// Add a simple tool for demonstration
server.tool(
  "greet",
  {
    name: z.string().describe("Name to greet"),
  },
  async ({ name }) => {
    return {
      content: [
        {
          type: "text",
          text: `Hello, ${name}! This is Roo's MCP server.`,
        },
      ],
    };
  }
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('Roo MCP server running on stdio');