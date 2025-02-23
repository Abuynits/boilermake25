'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import styles from './styles.module.css';

// Dynamically import Monaco Editor
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

interface DeleteConfirmation {
  fileName: string;
  x: number;
  y: number;
}


// Unique list of supported languages with their display names
const SUPPORTED_LANGUAGES = [
  { id: 'python', name: 'Python' },
  { id: 'javascript', name: 'JavaScript' },
  { id: 'typescript', name: 'TypeScript' },
  { id: 'html', name: 'HTML' },
  { id: 'css', name: 'CSS' },
  { id: 'json', name: 'JSON' },
  { id: 'markdown', name: 'Markdown' },
  { id: 'sql', name: 'SQL' },
  { id: 'java', name: 'Java' },
  { id: 'cpp', name: 'C++' },
  { id: 'c', name: 'C' },
  { id: 'go', name: 'Go' },
  { id: 'rust', name: 'Rust' },
  { id: 'ruby', name: 'Ruby' },
  { id: 'php', name: 'PHP' },
  { id: 'plaintext', name: 'Plain Text' },
];

// Map file extensions to language IDs
const LANGUAGE_MAP: { [key: string]: string } = {
  'py': 'python',
  'js': 'javascript',
  'ts': 'typescript',
  'jsx': 'javascript',
  'tsx': 'typescript',
  'html': 'html',
  'css': 'css',
  'json': 'json',
  'md': 'markdown',
  'sql': 'sql',
  'java': 'java',
  'cpp': 'cpp',
  'c': 'c',
  'go': 'go',
  'rs': 'rust',
  'rb': 'ruby',
  'php': 'php',
  'txt': 'plaintext'
};

const FILE_ICONS: { [key: string]: JSX.Element | string } = {
  // Programming Languages
  'py': '<i class="devicon-python-plain colored"></i>',
  'js': '<i class="devicon-javascript-plain colored"></i>',
  'ts': '<i class="devicon-typescript-plain colored"></i>',
  'jsx': '<i class="devicon-react-original colored"></i>',
  'tsx': '<i class="devicon-react-original colored"></i>',
  'html': '<i class="devicon-html5-plain colored"></i>',
  'css': '<i class="devicon-css3-plain colored"></i>',
  'java': '<i class="devicon-java-plain colored"></i>',
  'cpp': '<i class="devicon-cplusplus-plain colored"></i>',
  'c': '<i class="devicon-c-plain colored"></i>',
  'go': '<i class="devicon-go-plain colored"></i>',
  'rs': '<i class="devicon-rust-plain colored"></i>',
  'rb': '<i class="devicon-ruby-plain colored"></i>',
  'php': '<i class="devicon-php-plain colored"></i>',
  
  // Data & Config Files
  'json': '<svg class="w-5 h-5 text-yellow-600" viewBox="0 0 24 24" fill="currentColor"><path d="M4 14.745c0 1.103.896 2 2 2h12c1.104 0 2-.897 2-2v-5.49c0-1.103-.896-2-2-2H6c-1.104 0-2 .897-2 2v5.49z"/><path d="M6 18.745h12v-3H6v3zm0-11.49h12v-3H6v3z"/></svg>',
  'md': '<svg class="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="currentColor"><path d="M14.345 6h-4.69c-.241 0-.437.196-.437.437v11.126c0 .241.196.437.437.437h4.69c.241 0 .437-.196.437-.437V6.437c0-.241-.196-.437-.437-.437zM7.5 6h-3c-.276 0-.5.224-.5.5v10c0 .276.224.5.5.5h3c.276 0 .5-.224.5-.5v-10c0-.276-.224-.5-.5-.5zM19.5 6h-3c-.276 0-.5.224-.5.5v10c0 .276.224.5.5.5h3c.276 0 .5-.224.5-.5v-10c0-.276-.224-.5-.5-.5z"/></svg>',
  'sql': '<svg class="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="currentColor"><path d="M4 5h16v2H4zm0 6h16v2H4zm0 6h16v2H4z"/></svg>',
  'txt': '<svg class="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 1v5h5v10H6V3h7z"/></svg>',
  'default': '<svg class="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 1v5h5v10H6V3h7z"/></svg>'
};

interface File {
  name: string;
  content: string;
  language: string;
}

interface Tab {
  id: string;
  name: string;
  language: string;
}

export default function CodeEditor() {
  const outputRef = useRef<HTMLDivElement>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState<DeleteConfirmation | null>(null);
  const [showNewFileDialog, setShowNewFileDialog] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [files, setFiles] = useState<File[]>([
    {
      name: 'main.py',
      content: '# Write your code here\nprint("Hello, World!")',
      language: 'python'
    }
  ]);

  const [openTabs, setOpenTabs] = useState<Tab[]>([
    { id: 'main.py', name: 'main.py', language: 'python' }
  ]);

  const [activeTab, setActiveTab] = useState('main.py');
  const [code, setCode] = useState(files[0].content);
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);

  const handleFileClick = (file: File) => {
    // Open the file in a new tab if not already open
    if (!openTabs.find(tab => tab.id === file.name)) {
      setOpenTabs([...openTabs, { id: file.name, name: file.name, language: file.language }]);
    }
    setActiveTab(file.name);
    setCode(file.content);
  };

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    const file = files.find(f => f.name === tabId);
    if (file) {
      setCode(file.content);
    }
  };

  const handleCloseTab = (tabId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const newTabs = openTabs.filter(tab => tab.id !== tabId);
    if (newTabs.length === 0) {
      // Keep at least one tab open
      return;
    }
    setOpenTabs(newTabs);
    if (activeTab === tabId) {
      setActiveTab(newTabs[0].id);
      const file = files.find(f => f.name === newTabs[0].id);
      if (file) {
        setCode(file.content);
      }
    }
  };

  const handleCodeChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    // Update file content
    const fileIndex = files.findIndex(f => f.name === activeTab);
    if (fileIndex !== -1) {
      const newFiles = [...files];
      newFiles[fileIndex] = { ...newFiles[fileIndex], content: newCode };
      setFiles(newFiles);
    }
  };

  // Update code when active tab changes
  useEffect(() => {
    const file = files.find(f => f.name === activeTab);
    if (file) {
      setCode(file.content);
    }
  }, [activeTab, files]);

  // Scroll output to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const handleRunCode = async () => {
    setIsExecuting(true);
    setOutput('');
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/execute-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          code,
          language: activeTab ? activeTab.split('.').pop() || 'python' : 'python'
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setOutput(data.output);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to execute code. Please try again.');
      console.error(err)
    } finally {
      setIsExecuting(false);
    }
  };

  const getFileIcon = (fileName: string): JSX.Element | string => {
    const extension = fileName.split('.').pop() || '';
    return FILE_ICONS[extension] || FILE_ICONS.default;
  };

  const handleCreateFile = () => {
    if (!newFileName) return;
    
    // Add extension if not provided
    let finalName = newFileName;
    if (!finalName.includes('.')) {
      finalName += '.py';
    }

    // Check if file already exists
    if (files.some(f => f.name === finalName)) {
      alert('A file with this name already exists!');
      return;
    }

    const extension = finalName.split('.').pop() || '';
    const newFile: File = {
      name: finalName,
      content: '',
      language: LANGUAGE_MAP[extension] || 'plaintext'
    };

    setFiles([...files, newFile]);
    setOpenTabs([...openTabs, { id: finalName, name: finalName, language: newFile.language }]);
    setActiveTab(finalName);
    setCode(''); // Reset code state when creating new file
    setShowNewFileDialog(false);
    setNewFileName('');
  };

  const handleDeleteClick = (fileName: string, event: React.MouseEvent) => {
    event.stopPropagation();
    event.preventDefault();
    
    if (files.length <= 1) {
      alert('Cannot delete the last file!');
      return;
    }

    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    setDeleteConfirmation({
      fileName,
      x: rect.left,
      y: rect.bottom + 5
    });
  };

  const handleDeleteConfirm = (fileName: string) => {
    const newFiles = files.filter(f => f.name !== fileName);
    setFiles(newFiles);

    // Close tab if open
    const newTabs = openTabs.filter(tab => tab.id !== fileName);
    setOpenTabs(newTabs);

    // Switch to another tab if the active tab was deleted
    if (activeTab === fileName) {
      setActiveTab(newTabs[0].id);
      const firstFile = newFiles[0];
      if (firstFile) {
        setCode(firstFile.content);
      }
    }
    setDeleteConfirmation(null);
  };

  return (
    <div className={styles.editorContainer}>
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>Files</div>
        <div className={styles.sidebarActions}>
          <button
            className={styles.newFileButton}
            onClick={() => setShowNewFileDialog(true)}
          >
            + New File
          </button>
        </div>
        {showNewFileDialog && (
          <div className={styles.newFileDialog}>
            <input
              type="text"
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              placeholder="filename.py"
              className={styles.newFileInput}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateFile();
                if (e.key === 'Escape') {
                  setShowNewFileDialog(false);
                  setNewFileName('');
                }
              }}
            />
            <div className={styles.newFileActions}>
              <button
                className={styles.createButton}
                onClick={handleCreateFile}
              >
                Create
              </button>
              <button
                className={styles.cancelButton}
                onClick={() => {
                  setShowNewFileDialog(false);
                  setNewFileName('');
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
        <div className={styles.fileList}>
          {files.map((file) => (
            <div
              key={file.name}
              className={`${styles.file} ${activeTab === file.name ? styles.activeFile : ''}`}
              onClick={() => handleFileClick(file)}
            >
              <span className={styles.fileIcon} dangerouslySetInnerHTML={{ __html: getFileIcon(file.name) }} />
              <span className={styles.fileName}>{file.name}</span>
              <button
                className={styles.deleteFile}
                onClick={(e) => handleDeleteClick(file.name, e)}
                title="Delete file"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.mainContent}>
        <div className={styles.tabs}>
          {openTabs.map((tab) => (
            <div
              key={tab.id}
              className={`${styles.tab} ${activeTab === tab.id ? styles.activeTab : ''}`}
              onClick={() => handleTabClick(tab.id)}
            >
              {tab.name}
              <button
                className={styles.closeTab}
                onClick={(e) => handleCloseTab(tab.id, e)}
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <div className={styles.editor}>
          <div className={styles.editorHeader}>
            <select
              className={styles.languageSelect}
              value={openTabs.find(tab => tab.id === activeTab)?.language || 'python'}
              onChange={(e) => {
                const newLang = e.target.value;
                const fileIndex = files.findIndex(f => f.name === activeTab);
                if (fileIndex !== -1) {
                  const newFiles = [...files];
                  newFiles[fileIndex] = { ...newFiles[fileIndex], language: newLang };
                  setFiles(newFiles);
                  
                  const tabIndex = openTabs.findIndex(tab => tab.id === activeTab);
                  if (tabIndex !== -1) {
                    const newTabs = [...openTabs];
                    newTabs[tabIndex] = { ...newTabs[tabIndex], language: newLang };
                    setOpenTabs(newTabs);
                  }
                }
              }}
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.id} value={lang.id}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
          <MonacoEditor
            height="400px"
            language={openTabs.find(tab => tab.id === activeTab)?.language || 'python'}
            value={code}
            theme="vs-dark"
            onChange={handleCodeChange}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              lineNumbers: 'on',
              roundedSelection: false,
              selectOnLineNumbers: true,
              quickSuggestions: true,
            }}
          />
        </div>

        <div className={styles.outputPanel}>
          <div className={styles.outputHeader}>
            <h3>Output</h3>
            <button
              onClick={handleRunCode}
              className={styles.runButton}
              disabled={isExecuting}
            >
              {isExecuting ? 'Running...' : 'Run Code'}
            </button>
          </div>
          <div className={styles.outputContent} ref={outputRef}>
            {output && <pre className={styles.output}>{output}</pre>}
            {error && <pre className={styles.error}>{error}</pre>}
            {!output && !error && (
              <div className={styles.placeholder}>Run your code to see the output here</div>
            )}
          </div>
        </div>
      </div>
      {deleteConfirmation && (
        <>
          <div 
            className={styles.overlay}
            onClick={() => setDeleteConfirmation(null)}
          />
          <div 
            className={styles.confirmDialog}
            style={{
              left: `${deleteConfirmation.x}px`,
              top: `${deleteConfirmation.y}px`
            }}
          >
            <p className={styles.confirmText}>Delete {deleteConfirmation.fileName}?</p>
            <div className={styles.confirmActions}>
              <button
                className={styles.confirmButton}
                onClick={() => handleDeleteConfirm(deleteConfirmation.fileName)}
              >
                Delete
              </button>
              <button
                className={styles.cancelButton}
                onClick={() => setDeleteConfirmation(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
