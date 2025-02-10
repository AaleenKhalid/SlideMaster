const API_URL = 'http://localhost:5000/api/slides/generate';

export async function generateSlides(prompt) {
    try {
        const response = await fetch(API_URL, {
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

        const data = await response.json();

        if (!data.markdown) {
            throw new Error('No markdown content received');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw new Error(error.message || 'Failed to generate slides');
    }
}