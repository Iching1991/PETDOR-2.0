// src/services/api.ts
/**
 * Serviço de integração com backend PETdor (Streamlit/Python)
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8501/api";

interface AssessmentData {
  ownerName: string;
  ownerEmail: string;
  petName: string;
  petSpecies: string;
  petBreed: string;
  petAge: string;
  painLevel: string;
  clinicalSigns: string;
  observations: string;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * Envia avaliação de dor para o backend
 */
export const submitAssessment = async (
  assessment: AssessmentData,
  token: string
): Promise<ApiResponse<{ pdf_url: string; assessment_id: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/assessment/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        tutor_nome: assessment.ownerName,
        tutor_email: assessment.ownerEmail,
        pet_nome: assessment.petName,
        pet_especie: assessment.petSpecies,
        pet_raca: assessment.petBreed,
        pet_idade: assessment.petAge,
        nivel_dor: parseInt(assessment.painLevel),
        sinais_clinicos: assessment.clinicalSigns,
        observacoes: assessment.observations,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao enviar avaliação:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro desconhecido",
    };
  }
};

/**
 * Faz login do usuário
 */
export const login = async (
  email: string,
  password: string
): Promise<ApiResponse<{ token: string; user: { id: string; nome: string; email: string } }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        senha: password,
      }),
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao fazer login:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro ao fazer login",
    };
  }
};

/**
 * Registra novo usuário
 */
export const register = async (
  nome: string,
  email: string,
  password: string,
  tipo: "tutor" | "clinica" | "veterinario"
): Promise<ApiResponse<{ user_id: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        nome,
        email,
        senha: password,
        tipo,
      }),
    });

    if (!response.ok) {
      throw new Error(`Registration failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao registrar:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro ao registrar",
    };
  }
};

/**
 * Solicita reset de senha
 */
export const requestPasswordReset = async (
  email: string
): Promise<ApiResponse<{ message: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset/request`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao solicitar reset:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro ao solicitar reset",
    };
  }
};

/**
 * Redefine senha com token
 */
export const resetPassword = async (
  token: string,
  newPassword: string
): Promise<ApiResponse<{ message: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset/confirm`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        token,
        nova_senha: newPassword,
      }),
    });

    if (!response.ok) {
      throw new Error(`Reset failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao redefinir senha:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro ao redefinir senha",
    };
  }
};

/**
 * Obtém histórico de avaliações do usuário
 */
export const getAssessmentHistory = async (
  token: string
): Promise<ApiResponse<Array<{ id: string; pet_nome: string; data: string; nivel_dor: number }>>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/assessment/history`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Fetch failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao buscar histórico:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Erro ao buscar histórico",
    };
  }
};

export default {
  submitAssessment,
  login,
  register,
  requestPasswordReset,
  resetPassword,
  getAssessmentHistory,
};

