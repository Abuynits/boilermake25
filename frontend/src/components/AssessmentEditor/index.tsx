'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import Monaco Editor
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function AssessmentEditor() {
  const [codeFilePath, setCodeFilePath] = useState('');
  const [repoName, setRepoName] = useState('');
  const [userAnswer, setUserAnswer] = useState('');
  const [codeContent, setCodeContent] = useState('// Code will appear here');
  const [editorKey, setEditorKey] = useState(0);

  // Force editor to reinitialize after a delay
  useEffect(() => {
    const timer = setTimeout(() => {
      setEditorKey(prev => prev + 1);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const handleScore = async () => {
    // TODO: Implement scoring logic
    console.log('Scoring submission...');
  };

  return (
    <div className="flex flex-col w-full gap-4 p-4">
      <div className="flex gap-4 h-[500px]">
        {/* Left Panel - Read Only Code */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 rounded-lg overflow-hidden border border-gray-200">
            <MonacoEditor
              key={editorKey}
              height="100%"
              defaultLanguage="javascript"
              value={codeContent}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 14,
                theme: 'vs-dark'
              }}
              className="min-h-[200px]"
              onMount={(editor, monaco) => {
                monaco.editor.setTheme('vs-dark');
                editor.updateOptions({
                  theme: 'vs-dark'
                });
              }}
            />
          </div>
          <div className="mt-4 flex flex-col gap-2">
            <div className="text-gray-900 border border-gray-200 rounded-md px-4 py-2">
              Code file path {codeFilePath ? `(${codeFilePath})` : '(not specified)'}
            </div>
            <div className="text-gray-900 border border-gray-200 rounded-md px-4 py-2">
              Repo name {repoName ? `(${repoName})` : '(not specified)'}
            </div>
          </div>
        </div>

        {/* Right Panel - User Answer */}
        <div className="flex-1 flex flex-col">
          <textarea
            className="flex-1 p-4 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
            placeholder="Enter your answer here..."
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            style={{ height: 'calc(100% - 48px)' }}
          />
        </div>
      </div>
      
      {/* Score Button - Below both panels */}
      <div className="flex justify-end mt-2">
        <button
          onClick={handleScore}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Score
        </button>
      </div>
    </div>
  );
}
