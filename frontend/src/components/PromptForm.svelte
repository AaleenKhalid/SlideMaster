<script>
    import { generateSlides } from '$lib/api.js';
    import { marked } from 'marked';

    //let prompt = '';
    let generatedMarkdown = '';
    let error = '';
    let isLoading = false;
    let slideDeckLength = '';
    let detailLevel = '';
    let textTone = '';
    let topicHeading = '';
    let keyPoints = ''; // TODO - might need to update structure


    async function handleSubmit() {
        error = '';
        generatedMarkdown = '';
        isLoading = true;

        try {
            const response = await generateSlides(prompt);
            generatedMarkdown = response.markdown;
        } catch (err) {
            error = err.message || 'Failed to generate slides';
        } finally {
            isLoading = false;
        }
    }
    // $ means it's a reactive statement
    $: parsedMarkdown = generatedMarkdown ? marked(generatedMarkdown) : ''; // converting markdown to HTML using marked()
</script>

<div class="prompt-form">
    <form on:submit|preventDefault={handleSubmit}>


        <textarea
                bind:value={keyPoints}
                placeholder="Enter your slide deck requirements..."
                rows="4"
                required
        ></textarea>


        <button type="submit" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Slides with Gemma2'}
        </button>
    </form>

    {#if error}
        <div class="error">{error}</div>
    {/if}

    {#if generatedMarkdown}
        <div class="markdown-output">
            <h3>Generated Slides:</h3>
            <div class="markdown-content">
                {@html parsedMarkdown}
            </div>
            <div class="raw-markdown">
                <h4>Raw Markdown:</h4>
                <pre>{generatedMarkdown}</pre>
            </div>
        </div>
    {/if}
</div>

<style>
    .prompt-form {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }

    textarea {
        width: 100%;
        margin-bottom: 10px;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-height: 120px;
    }

    button {
        width: 100%;
        padding: 12px;
        margin-top: 10px;
    }

    .error {
        color: red;
        margin-top: 10px;
        padding: 10px;
        background-color: #ffebee;
        border-radius: 4px;
    }

    .markdown-output {
        margin-top: 30px;
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .markdown-content {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-bottom: 20px;
    }

    .raw-markdown {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }

    .raw-markdown pre {
        background-color: #f4f4f4;
        padding: 15px;
        border-radius: 4px;
        overflow-x: auto;
    }

    :global(.markdown-content h1) {
        color: #2c3e50;
        margin-top: 0;
    }

    :global(.markdown-content h2) {
        color: #34495e;
        margin-top: 1.5em;
    }

    :global(.markdown-content ul, .markdown-content ol) {
        padding-left: 20px;
    }

    :global(.markdown-content li) {
        margin: 8px 0;
    }
</style>