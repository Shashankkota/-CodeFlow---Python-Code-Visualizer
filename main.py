#!/usr/bin/env python3
"""
CodeFlow - Python Code Visualizer
Interactive code execution visualizer with enhanced input support
"""

import pygame
import sys
import time
import requests
import json
from typing import Dict, Any, List, Tuple


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (240, 240, 240)
BLUE = (0, 123, 255)
GREEN = (40, 167, 69)
RED = (220, 53, 69)
YELLOW = (255, 193, 7)
ORANGE = (255, 152, 0)
PURPLE = (102, 16, 242)
DARK_BLUE = (13, 110, 253)


class CodeFlowVisualizer:
    """Enhanced code visualizer with better input support"""
    
    def __init__(self):
        pygame.init()
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("CodeFlow - Python Code Visualizer")
        
        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        self.font_code = pygame.font.Font(None, 18)
        
        # State
        self.mode = "input"
        self.current_line = 0
        self.variables = {}
        self.execution_speed = 1.0
        self.auto_play = False
        self.is_running = False
        
        # Code input
        self.code_input = [
            "# Enter your Python code here:",
            "# Example:",
            "x = 10",
            "y = 20",
            "z = x + y",
            "print(f\"Sum: {z}\")",
            "",
            "# You can add more lines...",
            "for i in range(3):",
            "    print(f\"Count: {i}\")",
            "    result = i * 2",
            "    print(f\"Double: {result}\")"
        ]
        self.cursor_pos = [2, 0]
        self.cursor_blink = 0
        
        # Editor area
        self.editor_rect = pygame.Rect(20, 250, self.width - 40, 500)
        
        # Parsed code
        self.structured_lines = []
        
        # Groq API configuration
        self.groq_api_key = "YOUR_GROQ_API_KEY"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.explanations = []
        self.current_explanation = ""
        
    def _parse_code(self):
        """Parse code into structured format"""
        structured = []
        for i, line in enumerate(self.code_input):
            if not line.strip():
                continue
                
            indent = len(line) - len(line.lstrip())
            node_type = self._get_node_type(line)
            
            structured.append({
                'line_number': i + 1,
                'content': line,
                'indent': indent // 4,
                'node_type': node_type,
                'is_current': False,
                'is_executed': False
            })
        return structured
    
    def _get_node_type(self, line: str) -> str:
        """Get node type for line"""
        line = line.strip()
        if line.startswith('#'):
            return 'comment'
        elif line.startswith('def '):
            return 'function_def'
        elif line.startswith('for '):
            return 'for_loop'
        elif line.startswith('if '):
            return 'if_statement'
        elif line.startswith('print('):
            return 'print_statement'
        elif '=' in line and not line.startswith('#'):
            return 'assignment'
        else:
            return 'expression'
    
    def _get_char_at_pos(self, pos):
        """Convert mouse position to cursor position"""
        if not self.editor_rect.collidepoint(pos):
            return None
        
        x, y = pos
        rel_x = x - self.editor_rect.x
        rel_y = y - self.editor_rect.y
        
        # Calculate line number
        line_num = int(rel_y // 25)  # 25 is line height
        if line_num >= len(self.code_input):
            line_num = len(self.code_input) - 1
        
        # Calculate character position
        char_pos = int((rel_x - 60) // 8)  # 60 for line numbers, 8 for char width
        if char_pos < 0:
            char_pos = 0
        
        line = self.code_input[line_num]
        if char_pos > len(line):
            char_pos = len(line)
        
        return [line_num, char_pos]
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            self.cursor_blink += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos)
            
            self._update(dt)
            self._draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _handle_key(self, key):
        """Handle keyboard input"""
        if self.mode == "input":
            self._handle_input_key(key)
        else:
            self._handle_visualize_key(key)
    
    def _handle_input_key(self, key):
        """Handle keys in input mode"""
        # Get modifier keys
        mods = pygame.key.get_mods()
        
        # Handle Ctrl+C for exit
        if mods & pygame.KMOD_CTRL and key == pygame.K_c:
            pygame.quit()
            sys.exit()
        
        # Ignore other Ctrl key combinations
        if mods & pygame.KMOD_CTRL:
            return
        
        if key == pygame.K_RETURN:
            # Add new line
            self.code_input.insert(self.cursor_pos[0] + 1, "")
            self.cursor_pos[0] += 1
            self.cursor_pos[1] = 0
        elif key == pygame.K_BACKSPACE:
            if self.cursor_pos[1] > 0:
                # Delete character
                line = self.code_input[self.cursor_pos[0]]
                self.code_input[self.cursor_pos[0]] = line[:self.cursor_pos[1]-1] + line[self.cursor_pos[1]:]
                self.cursor_pos[1] -= 1
            elif self.cursor_pos[0] > 0:
                # Delete line
                if self.code_input[self.cursor_pos[0]]:
                    self.code_input[self.cursor_pos[0]-1] += self.code_input[self.cursor_pos[0]]
                self.code_input.pop(self.cursor_pos[0])
                self.cursor_pos[0] -= 1
                self.cursor_pos[1] = len(self.code_input[self.cursor_pos[0]])
        elif key == pygame.K_DELETE:
            # Delete character at cursor
            line = self.code_input[self.cursor_pos[0]]
            if self.cursor_pos[1] < len(line):
                self.code_input[self.cursor_pos[0]] = line[:self.cursor_pos[1]] + line[self.cursor_pos[1]+1:]
        elif key == pygame.K_LEFT:
            if self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
        elif key == pygame.K_RIGHT:
            line = self.code_input[self.cursor_pos[0]]
            if self.cursor_pos[1] < len(line):
                self.cursor_pos[1] += 1
        elif key == pygame.K_UP:
            if self.cursor_pos[0] > 0:
                self.cursor_pos[0] -= 1
                self.cursor_pos[1] = min(self.cursor_pos[1], len(self.code_input[self.cursor_pos[0]]))
        elif key == pygame.K_DOWN:
            if self.cursor_pos[0] < len(self.code_input) - 1:
                self.cursor_pos[0] += 1
                self.cursor_pos[1] = min(self.cursor_pos[1], len(self.code_input[self.cursor_pos[0]]))
        elif key == pygame.K_TAB:
            # Add 4 spaces
            line = self.code_input[self.cursor_pos[0]]
            self.code_input[self.cursor_pos[0]] = line[:self.cursor_pos[1]] + "    " + line[self.cursor_pos[1]:]
            self.cursor_pos[1] += 4
        elif key == pygame.K_F5:
            # Start visualization
            self._start_visualization()
        else:
            # Handle special characters
            char = self._get_char_from_key(key)
            if char:
                line = self.code_input[self.cursor_pos[0]]
                self.code_input[self.cursor_pos[0]] = line[:self.cursor_pos[1]] + char + line[self.cursor_pos[1]:]
                self.cursor_pos[1] += 1
    
    def _get_char_from_key(self, key):
        """Convert key to character with special handling"""
        # Get modifier keys
        mods = pygame.key.get_mods()
        
        # Handle special characters with shift
        if mods & pygame.KMOD_SHIFT:
            shift_chars = {
                pygame.K_1: '!',
                pygame.K_2: '@',
                pygame.K_3: '#',
                pygame.K_4: '$',
                pygame.K_5: '%',
                pygame.K_6: '^',
                pygame.K_7: '&',
                pygame.K_8: '*',
                pygame.K_9: '(',
                pygame.K_0: ')',
                pygame.K_MINUS: '_',
                pygame.K_EQUALS: '+',
                pygame.K_LEFTBRACKET: '{',
                pygame.K_RIGHTBRACKET: '}',
                pygame.K_BACKSLASH: '|',
                pygame.K_SEMICOLON: ':',
                pygame.K_QUOTE: '"',
                pygame.K_COMMA: '<',
                pygame.K_PERIOD: '>',
                pygame.K_SLASH: '?',
                pygame.K_BACKQUOTE: '~',
            }
            if key in shift_chars:
                return shift_chars[key]
        
        # Handle special characters without shift
        special_chars = {
            pygame.K_PERIOD: '.',
            pygame.K_COMMA: ',',
            pygame.K_SEMICOLON: ';',
            pygame.K_COLON: ':',
            pygame.K_QUOTE: "'",
            pygame.K_QUOTEDBL: '"',
            pygame.K_LEFTBRACKET: '[',
            pygame.K_RIGHTBRACKET: ']',
            pygame.K_LEFTPAREN: '(',
            pygame.K_RIGHTPAREN: ')',
            pygame.K_EQUALS: '=',
            pygame.K_PLUS: '+',
            pygame.K_MINUS: '-',
            pygame.K_ASTERISK: '*',
            pygame.K_SLASH: '/',
            pygame.K_BACKSLASH: '\\',
            pygame.K_HASH: '#',
            pygame.K_AT: '@',
            pygame.K_EXCLAMATION: '!',
            pygame.K_QUESTION: '?',
            pygame.K_UNDERSCORE: '_',
            pygame.K_DOLLAR: '$',
            pygame.K_PERCENT: '%',
            pygame.K_AMPERSAND: '&',
            pygame.K_CARET: '^',
            pygame.K_TILDE: '~',
            pygame.K_LESS: '<',
            pygame.K_GREATER: '>',
            pygame.K_BAR: '|',
        }
        
        if key in special_chars:
            return special_chars[key]
        elif key < 256:
            return chr(key)
        else:
            return None
    
    def _handle_visualize_key(self, key):
        """Handle keys in visualize mode"""
        if key == pygame.K_SPACE:
            self.step_execution()
        elif key == pygame.K_r:
            self.run_execution()
        elif key == pygame.K_p:
            self.pause_execution()
        elif key == pygame.K_BACKSPACE:
            self.reset_execution()
        elif key == pygame.K_UP:
            self.execution_speed = max(0.1, self.execution_speed - 0.1)
        elif key == pygame.K_DOWN:
            self.execution_speed = min(2.0, self.execution_speed + 0.1)
        elif key == pygame.K_F5:
            # Back to input mode
            self.mode = "input"
            self._reset_visualization()
    
    def _handle_click(self, pos):
        """Handle mouse clicks"""
        if self.mode == "input":
            # Check for "Start Visualization" button
            button_rect = pygame.Rect(self.width - 200, 20, 180, 40)
            if button_rect.collidepoint(pos):
                self._start_visualization()
            else:
                # Handle mouse cursor positioning
                cursor_pos = self._get_char_at_pos(pos)
                if cursor_pos:
                    self.cursor_pos = cursor_pos
        else:
            # Check button clicks for visualization
            button_rects = {
                'step': pygame.Rect(50, self.height - 120, 100, 40),
                'run': pygame.Rect(160, self.height - 120, 100, 40),
                'pause': pygame.Rect(270, self.height - 120, 100, 40),
                'reset': pygame.Rect(380, self.height - 120, 100, 40),
                'back': pygame.Rect(490, self.height - 120, 100, 40),
            }
            
            for name, rect in button_rects.items():
                if rect.collidepoint(pos):
                    if name == 'step':
                        self.step_execution()
                    elif name == 'run':
                        self.run_execution()
                    elif name == 'pause':
                        self.pause_execution()
                    elif name == 'reset':
                        self.reset_execution()
                    elif name == 'back':
                        self.mode = "input"
                        self._reset_visualization()
    
    def _start_visualization(self):
        """Start visualization mode"""
        self.mode = "visualize"
        self.structured_lines = self._parse_code()
        self.current_line = 0
        self.variables = {}
        self.is_running = False
        self.auto_play = False
        self.explanations = []
        self.current_explanation = ""
        
        # Generate explanations for all lines
        self._generate_explanations()
        
        for line in self.structured_lines:
            line['is_current'] = False
            line['is_executed'] = False
    
    def _reset_visualization(self):
        """Reset visualization state"""
        self.current_line = 0
        self.variables = {}
        self.is_running = False
        self.auto_play = False
        
        for line in self.structured_lines:
            line['is_current'] = False
            line['is_executed'] = False
    
    def step_execution(self):
        """Execute next line"""
        if not self.is_running:
            self.is_running = True
            self.current_line = 0
        
        if self.current_line < len(self.structured_lines):
            self._execute_line(self.current_line)
            self.current_explanation = self._get_current_explanation()
            self.current_line += 1
    
    def run_execution(self):
        """Run all remaining lines"""
        if not self.is_running:
            self.step_execution()
        self.auto_play = True
    
    def pause_execution(self):
        """Pause execution"""
        self.auto_play = False
    
    def reset_execution(self):
        """Reset execution"""
        self._reset_visualization()
    
    def _execute_line(self, line_index: int):
        """Execute a specific line"""
        if line_index >= len(self.structured_lines):
            return
        
        line = self.structured_lines[line_index]
        line['is_current'] = True
        line['is_executed'] = True
        
        # Simulate execution
        content = line['content'].strip()
        if line['node_type'] == 'assignment':
            self._handle_assignment(content)
        elif line['node_type'] == 'print_statement':
            # Simulate print
            pass
    
    def _handle_assignment(self, content: str):
        """Handle variable assignment"""
        if '=' in content:
            var_name = content.split('=')[0].strip()
            value_part = content.split('=')[1].strip()
            
            try:
                if '+' in value_part and not value_part.startswith('"'):
                    # Simple arithmetic
                    parts = value_part.split('+')
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        if left.isdigit() and right.isdigit():
                            actual_value = int(left) + int(right)
                        else:
                            actual_value = value_part
                    else:
                        actual_value = value_part
                elif value_part.isdigit():
                    actual_value = int(value_part)
                elif value_part.replace('.', '').replace('-', '').isdigit():
                    actual_value = float(value_part)
                elif value_part.startswith('"') or value_part.startswith("'"):
                    actual_value = value_part.strip('"\'')
                else:
                    actual_value = value_part
                
                self.variables[var_name] = {
                    'value': actual_value,
                    'type': type(actual_value).__name__,
                    'line': self.structured_lines[self.current_line]['line_number']
                }
                
            except:
                pass
    
    def _update(self, dt: float):
        """Update game state"""
        if self.mode == "visualize" and self.auto_play and self.is_running:
            current_time = time.time()
            if not hasattr(self, '_last_step_time'):
                self._last_step_time = current_time
            
            if current_time - self._last_step_time >= self.execution_speed:
                self.step_execution()
                self._last_step_time = current_time
    
    def _draw(self):
        """Draw everything"""
        self.screen.fill(WHITE)
        
        if self.mode == "input":
            self._draw_input_mode()
        else:
            self._draw_visualize_mode()
    
    def _draw_input_mode(self):
        """Draw input mode"""
        # Draw title
        title = self.font_large.render("CodeFlow - Python Code Visualizer", True, BLACK)
        self.screen.blit(title, (20, 20))
        
        # Draw instructions
        instructions = [
            "Enhanced Features:",
            "- Click anywhere in the editor to position cursor",
            "- Special characters: () [] {} = + - * / # @ ! ? _ $ % & ^ ~ < > |",
            "- Use Tab for indentation",
            "- Press F5 or click 'Start Visualization' to begin",
            "- Press Ctrl+C to exit"
        ]
        
        y_offset = 80
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, BLACK)
            self.screen.blit(text, (20, y_offset))
            y_offset += 30
        
        # Draw code input area
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.editor_rect)
        pygame.draw.rect(self.screen, BLACK, self.editor_rect, 2)
        
        # Draw code lines
        y_offset = 270
        for i, line in enumerate(self.code_input):
            if y_offset > 720:
                break
            
            # Line number
            line_num = self.font_code.render(f"{i+1:2d}", True, GRAY)
            self.screen.blit(line_num, (40, y_offset))
            
            # Line content
            text = self.font_code.render(line, True, BLACK)
            self.screen.blit(text, (80, y_offset))
            
            # Draw cursor
            if i == self.cursor_pos[0] and int(self.cursor_blink * 2) % 2:
                cursor_surface = self.font_code.render(line[:self.cursor_pos[1]], True, BLACK)
                cursor_x = 80 + cursor_surface.get_width()
                pygame.draw.line(self.screen, BLACK, (cursor_x, y_offset), (cursor_x, y_offset + 20), 2)
            
            y_offset += 25
        
        # Draw "Start Visualization" button
        button_rect = pygame.Rect(self.width - 200, 20, 180, 40)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        text = self.font_medium.render("Start Visualization (F5)", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
    
    def _draw_visualize_mode(self):
        """Draw visualization mode"""
        # Draw title
        title = self.font_large.render("CodeFlow - Code Visualization", True, BLACK)
        self.screen.blit(title, (20, 20))
        
        # Draw code panel
        self._draw_code_panel()
        
        # Draw variables panel
        self._draw_variables_panel()
        
        # Draw explanations panel
        self._draw_explanations_panel()
        
        # Draw control panel
        self._draw_control_panel()
        
        # Draw status
        self._draw_status()
    
    def _draw_code_panel(self):
        """Draw the code display panel"""
        panel_rect = pygame.Rect(20, 80, 700, 500)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Panel title
        title = self.font_medium.render("Code Execution", True, BLACK)
        self.screen.blit(title, (30, 90))
        
        # Draw code lines
        y_offset = 130
        for line in self.structured_lines:
            if y_offset > 550:
                break
            
            # Line number
            line_num = self.font_code.render(f"{line['line_number']:2d}", True, GRAY)
            self.screen.blit(line_num, (40, y_offset))
            
            # Indent
            indent_x = 80 + (line['indent'] * 20)
            
            # Line content
            color = BLACK
            if line['is_current']:
                # Highlight current line
                highlight_rect = pygame.Rect(indent_x - 5, y_offset - 2, 650, 22)
                pygame.draw.rect(self.screen, YELLOW, highlight_rect)
                color = BLACK
            elif line['is_executed']:
                color = GREEN
            
            # Node type indicator
            type_color = self._get_node_type_color(line['node_type'])
            type_indicator = pygame.Rect(indent_x - 15, y_offset + 8, 8, 8)
            pygame.draw.rect(self.screen, type_color, type_indicator)
            
            # Line text
            text = self.font_code.render(line['content'], True, color)
            self.screen.blit(text, (indent_x, y_offset))
            
            y_offset += 25
    
    def _draw_variables_panel(self):
        """Draw the variables panel"""
        panel_rect = pygame.Rect(740, 80, 640, 500)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Panel title
        title = self.font_medium.render("Variables & State", True, BLACK)
        self.screen.blit(title, (750, 90))
        
        # Draw variables
        y_offset = 130
        for name, var in self.variables.items():
            if y_offset > 550:
                break
            
            # Variable name
            name_text = self.font_code.render(f"{name}:", True, BLUE)
            self.screen.blit(name_text, (760, y_offset))
            
            # Variable value
            value_text = self.font_code.render(f"{var['value']} ({var['type']})", True, BLACK)
            self.screen.blit(value_text, (860, y_offset))
            
            # Line created
            line_text = self.font_code.render(f"Line {var['line']}", True, GRAY)
            self.screen.blit(line_text, (760, y_offset + 20))
            
            y_offset += 50
    
    def _draw_explanations_panel(self):
        """Draw the explanations panel"""
        panel_rect = pygame.Rect(20, 600, self.width - 40, 200)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Panel title
        title = self.font_medium.render("Step-by-Step Explanation", True, BLACK)
        self.screen.blit(title, (30, 610))
        
        # Draw current explanation
        if self.current_explanation:
            # Wrap text to fit panel width
            words = self.current_explanation.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                # Use render() to get text size
                test_surface = self.font_small.render(test_line, True, BLACK)
                if test_surface.get_width() < self.width - 60:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw explanation lines
            y_offset = 640
            for line in lines[:4]:  # Limit to 4 lines to fit panel
                text = self.font_small.render(line, True, BLACK)
                self.screen.blit(text, (30, y_offset))
                y_offset += 20
    
    def _draw_control_panel(self):
        """Draw the control buttons"""
        buttons = [
            ('Step (Space)', BLUE, pygame.Rect(50, self.height - 120, 100, 40)),
            ('Run (R)', GREEN, pygame.Rect(160, self.height - 120, 100, 40)),
            ('Pause (P)', ORANGE, pygame.Rect(270, self.height - 120, 100, 40)),
            ('Reset (Backspace)', RED, pygame.Rect(380, self.height - 120, 100, 40)),
            ('Back to Edit (F5)', PURPLE, pygame.Rect(490, self.height - 120, 100, 40)),
        ]
        
        for text, color, rect in buttons:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            text_surface = self.font_small.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_status(self):
        """Draw status information"""
        # Execution state
        state = "Running" if self.is_running else "Ready"
        state_text = self.font_medium.render(f"State: {state}", True, BLACK)
        self.screen.blit(state_text, (20, self.height - 80))
        
        # Current line
        if self.structured_lines and self.current_line < len(self.structured_lines):
            current_line = self.structured_lines[self.current_line]
            line_text = self.font_medium.render(f"Line: {current_line['line_number']}", True, BLACK)
            self.screen.blit(line_text, (200, self.height - 80))
        
        # Speed
        speed_text = self.font_medium.render(f"Speed: {self.execution_speed:.1f}s", True, BLACK)
        self.screen.blit(speed_text, (400, self.height - 80))
        
        # Progress
        if self.structured_lines:
            progress = (self.current_line / len(self.structured_lines)) * 100
            progress_text = self.font_medium.render(f"Progress: {progress:.1f}%", True, BLACK)
            self.screen.blit(progress_text, (600, self.height - 80))
    
    def _get_node_type_color(self, node_type: str) -> Tuple[int, int, int]:
        """Get color for node type"""
        colors = {
            'comment': GRAY,
            'function_def': BLUE,
            'for_loop': ORANGE,
            'if_statement': GREEN,
            'print_statement': DARK_BLUE,
            'assignment': BLACK,
            'expression': BLACK
        }
        return colors.get(node_type, BLACK)
    
    def _generate_explanations(self):
        """Generate step-by-step explanations using Groq API"""
        if not self.structured_lines:
            return
        
        # Prepare code for analysis
        code_lines = []
        for line in self.structured_lines:
            if line['content'].strip() and not line['content'].strip().startswith('#'):
                code_lines.append(f"Line {line['line_number']}: {line['content']}")
        
        if not code_lines:
            return
        
        code_text = "\n".join(code_lines)
        print(f"Generating explanations for code:\n{code_text}")
        
        # Create prompt for Groq API
        prompt = f"""Analyze this Python code and provide detailed, step-by-step explanations for each line of execution. 
        Explain what happens at each step in a simple, organized, and detailed way.
        
        Code:
        {code_text}
        
        Please provide explanations like:
        - "Here variable x is assigned the value 10"
        - "Variable y is assigned the value 20" 
        - "Variable z is calculated by adding x and y, resulting in 30"
        - "The print statement outputs the formatted string with the sum"
        - "The for loop starts, initializing i to 0"
        - "Inside the loop, i is 0, so 'Count: 0' is printed"
        - etc.
        
        Make each explanation clear, simple, and educational. Focus on what each line does and how variables change."""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.groq_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    explanation_text = result['choices'][0]['message']['content']
                    print(f"Groq API Response:\n{explanation_text}")
                    # Split explanations by lines
                    self.explanations = [exp.strip() for exp in explanation_text.split('\n') if exp.strip()]
                else:
                    self.explanations = ["Could not generate explanations"]
            else:
                self.explanations = [f"API Error: {response.status_code}"]
                
        except Exception as e:
            self.explanations = [f"Error generating explanations: {str(e)}"]
    
    def _get_current_explanation(self):
        """Get explanation for current line"""
        if self.current_line < len(self.explanations):
            return self.explanations[self.current_line]
        return "No explanation available for this line"


def main():
    """Main function"""
    visualizer = CodeFlowVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main() 
