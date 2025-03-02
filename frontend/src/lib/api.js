const API_URL = 'http://localhost:5000/api/slides';

export async function generateSlides(prompt) {
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to generate slides');
        }

        return response.json();

    } catch (error) {
        console.error('API Error:', error);
        throw new Error(error.message || 'Failed to generate slides');
    }
}