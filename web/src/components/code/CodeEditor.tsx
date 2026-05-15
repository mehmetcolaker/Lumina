/**
 * CodeMirror 6 editor component with syntax highlighting, line numbers,
 * bracket matching, and dark/light theme support.
 *
 * Usage:
 *   <CodeEditor
 *     value={code}
 *     onChange={setCode}
 *     language="python"
 *     readOnly={false}
 *     minHeight="300px"
 *   />
 */

import { useEffect, useRef } from "react";
import { EditorState } from "@codemirror/state";
import {
  EditorView,
  keymap,
  lineNumbers,
  highlightActiveLineGutter,
  highlightActiveLine,
  drawSelection,
} from "@codemirror/view";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import {
  bracketMatching,
  syntaxHighlighting,
  defaultHighlightStyle,
  indentOnInput,
} from "@codemirror/language";
import { closeBrackets, closeBracketsKeymap } from "@codemirror/autocomplete";
import { python } from "@codemirror/lang-python";
import { javascript } from "@codemirror/lang-javascript";

const LANG_MAP: Record<string, () => import("@codemirror/language").LanguageSupport> = {
  python: python,
  javascript: javascript,
  js: javascript,
  typescript: () => javascript({ typescript: true }),
  ts: () => javascript({ typescript: true }),
  jsx: () => javascript({ jsx: true }),
  tsx: () => javascript({ jsx: true, typescript: true }),
};

// ── Dark theme extension ──
const darkTheme = EditorView.theme(
  {
    "&": {
      backgroundColor: "#0d1117",
      color: "#e6edf3",
    },
    ".cm-gutters": {
      backgroundColor: "#0a0e16",
      color: "#484f58",
      border: "none",
      borderRight: "1px solid #21262d",
    },
    ".cm-activeLineGutter": {
      backgroundColor: "#1f2937",
    },
    ".cm-activeLine": {
      backgroundColor: "#1f293780",
    },
    ".cm-cursor": {
      borderLeftColor: "#58a6ff",
    },
    ".cm-selectionBackground, .cm-focused .cm-selectionBackground": {
      backgroundColor: "#264f78",
    },
    "&.cm-focused .cm-cursor": {
      borderLeftColor: "#58a6ff",
    },
  },
  { dark: true },
);

// ── Light theme extension ──
const lightTheme = EditorView.theme(
  {
    "&": {
      backgroundColor: "#ffffff",
      color: "#1f2328",
    },
    ".cm-gutters": {
      backgroundColor: "#f6f8fa",
      color: "#656d76",
      border: "none",
      borderRight: "1px solid #d0d7de",
    },
    ".cm-activeLineGutter": {
      backgroundColor: "#e8eaed",
    },
    ".cm-activeLine": {
      backgroundColor: "#f6f8fa",
    },
    ".cm-cursor": {
      borderLeftColor: "#0969da",
    },
    ".cm-selectionBackground, .cm-focused .cm-selectionBackground": {
      backgroundColor: "#accef7",
    },
    "&.cm-focused .cm-cursor": {
      borderLeftColor: "#0969da",
    },
  },
  { dark: false },
);

export interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  readOnly?: boolean;
  minHeight?: string;
  placeholder?: string;
  onLineClick?: (line: number) => void;
}

export function CodeEditor({
  value,
  onChange,
  language = "python",
  readOnly = false,
  minHeight = "300px",
  placeholder = "Kodunu buraya yaz...",
  onLineClick,
}: CodeEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);

  // Detect dark mode from <html> class
  const isDark =
    typeof document !== "undefined" && document.documentElement.classList.contains("dark");

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy previous view
    if (viewRef.current) {
      viewRef.current.destroy();
      viewRef.current = null;
    }

    // Get language extension
    const langKey = language.toLowerCase();
    const langExt = LANG_MAP[langKey]?.() ?? python();

    // Sync update listener
    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onChange(update.state.doc.toString());
      }
    });

    const extensions = [
      lineNumbers(),
      highlightActiveLineGutter(),
      highlightActiveLine(),
      drawSelection(),
      bracketMatching(),
      closeBrackets(),
      indentOnInput(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      history(),
      keymap.of([...defaultKeymap, ...historyKeymap, ...closeBracketsKeymap, indentWithTab]),
      langExt,
      updateListener,
      EditorView.lineWrapping,
      isDark ? darkTheme : lightTheme,
      EditorView.theme({
        "&": { minHeight, fontSize: "14px" },
        ".cm-scroller": { fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace' },
        "&.cm-focused": { outline: "none" },
      }),
    ];

    if (readOnly) {
      extensions.push(EditorView.editable.of(false));
    }

    const startState = EditorState.create({
      doc: value,
      extensions,
    });

    const view = new EditorView({
      state: startState,
      parent: containerRef.current,
    });

    // Add click handler for line numbers (comments)
    view.dom.addEventListener("click", (event) => {
      const target = event.target as HTMLElement;
      if (target.classList.contains("cm-lineNumbers") || target.closest(".cm-lineNumbers")) {
        const pos = view.posAtCoords({ x: event.clientX, y: event.clientY });
        if (pos != null) {
          const line = view.state.doc.lineAt(pos);
          onLineClick?.(line.number);
        }
      }
    });

    viewRef.current = view;

    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, readOnly, minHeight, isDark]);

  // Sync external value changes (reset, solution reveal)
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const current = view.state.doc.toString();
    if (current !== value) {
      view.dispatch({
        changes: {
          from: 0,
          to: current.length,
          insert: value,
        },
      });
    }
  }, [value]);

  return <div ref={containerRef} className="code-editor-container" style={{ minHeight }} />;
}
