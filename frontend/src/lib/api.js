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

/**
 * Export generated markdown content to Google Slides
 * @param {Object} data - Object containing markdown content and title
 * @returns {Promise<Object>} - Response with presentation URL
 */
export async function exportToGoogleSlides(data) {
    try {
        const response = await fetch('/api/slides/export-to-slides', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to export to Google Slides');
        }

        return await response.json();
    } catch (error) {
        console.error('Export to Google Slides error:', error);
        throw error;
    }
}