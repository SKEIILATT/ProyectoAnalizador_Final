export interface Token {
  type: string;
  value: string;
  line: number;
  column: number;
}

export interface Error {
  message: string;
  line: number;
  token?: string;
  char?: string;
  column?: number;
}

export interface Symbol {
  name: string;
  type: string;
  scope: string;
  line: number;
  is_const: boolean;
  return_type: string | null;
}

export interface Scope {
  level: number;
  symbols: Symbol[];
}

export interface AnalysisResult {
  lexico: {
    tokens: Token[];
    errores: Error[];
  };
  sintactico: {
    errores: Error[];
  };
  semantico: {
    errores: Error[];
    tabla_simbolos: Scope[];
  };
  filename?: string;
  code?: string;
}