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
    const url = `${API_URL}/export_to_slides`;
    console.log(`Making request to ${url}`);
    console.log(`Request data:`, data);

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        console.log('Request status:', response.status);

        if (!response.ok) {
            try{
                const errorData = await response.json();
                console.error('Error data: ', errorData);
                throw new Error(errorData.message || 'Failed to export to Google Slides');
            } catch (jsonError) {
                // if not JSON, get the text
                const errorText = await response.text();
                console.error('API Error:', errorText);
                throw new Error(errorText || 'Failed to export to Google Slides');
            }
        }

        const result = await response.json();
        console.log('Success response: ', result);
        return result;
    } catch (error) {
        console.error('Export to Google Slides error:', error);
        throw error;
    }
}