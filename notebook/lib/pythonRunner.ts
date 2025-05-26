import { spawn } from 'child_process';
import { writeFile, unlink } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';

export async function runPythonCode(code: string): Promise<{ success: boolean; output?: string; error?: string }> {
  // Create a temporary file to store the Python code
  const tempFile = join(tmpdir(), `python-${Date.now()}.py`);
  
  try {
    // Write the code to the temporary file
    await writeFile(tempFile, code);

    return new Promise((resolve) => {
      const pythonProcess = spawn('python', [tempFile]);
      let output = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', async (code) => {
        // Clean up the temporary file
        try {
          await unlink(tempFile);
        } catch (e) {
          console.error('Error deleting temporary file:', e);
        }

        if (code === 0) {
          resolve({ success: true, output });
        } else {
          resolve({ success: false, error });
        }
      });
    });
  } catch (error) {
    // Clean up the temporary file in case of error
    try {
      await unlink(tempFile);
    } catch (e) {
      console.error('Error deleting temporary file:', e);
    }
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
} 