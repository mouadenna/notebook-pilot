import { NextResponse } from 'next/server';
import { runPythonCode } from '@/lib/pythonRunner';

export async function POST(request: Request) {
  try {
    const { code } = await request.json();

    if (!code || typeof code !== 'string') {
      return NextResponse.json(
        { error: 'Code is required and must be a string' },
        { status: 400 }
      );
    }

    const result = await runPythonCode(code);
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error executing Python code:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 