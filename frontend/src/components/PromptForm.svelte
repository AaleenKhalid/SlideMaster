<script>
    import { generateSlides } from '$lib/api.js';
    import { exportToGoogleSlides } from '$lib/api.js';
    import { marked } from 'marked';
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    let prompt = '';
    let generatedMarkdown = '';
    let originalMarkdown = '';
    let error = '';
    let isLoading = false;
    let isExporting  = false;
    let slideDeckLength = 'moderate';
    let detailLevel = 'detailed';
    let textTone = 'formal';
    let topicHeading = '';
    let keyPoints = '';
    let showAnnotations = true;
    let verificationSummary = null;
    let exportSuccess = null;
    let exportedSlideUrl = '';

    // Option Settings
    const options = {
        slideDeckLength: [
            { value: '10-15', label: 'Short (10 -15 slides)' },
            { value: '15-35', label: 'Moderate (15 - 35 slides)' },
            { value: '35-50', label: 'Long (35 - 50 slides)' },
        ],

        detailLevel: [
            { value: 'brief', label: 'Brief', description: 'Key points only' },
            { value: 'standard', label: 'Standard', description: 'Balanced content' },
            { value: 'detailed', label: 'Detailed', description: 'In-depth content' }
        ],

        textTone: [
            { value: 'formal', label: 'Formal', description: 'More Professional' },
            { value: 'casual', label: 'Casual', description: 'Conversational style'},
            { value: 'academic', label: 'Academic', description: 'Teaching, research-style' },
        ]
    };

    // // Have active option section
    // let activeOption = 'slideDeckLength';
    //
    // function setActiveOption(option) {
    //     activeOption = option;
    // }
    //
    // function selectOption(setting, value) {
    //     if (setting === 'slideDeckLength') slideDeckLength = value;
    //     if (setting === 'detailLevel') detailLevel = value;
    //     if (setting === 'textTone') textTone = textTone;
    // }
    //
    // function getSelectedLabel(setting) {
    //     const selected = options[setting].find(opt =>
    //         opt.value === (setting === 'slideDeckLength') ? slideDeckLength : setting === 'detailLevel' ? detailLevel : textTone);
    //
    //     return selected ? selected.label : '';
    // }


    async function handleSubmit() {
        error = '';
        exportSuccess = null;
        exportedSlideUrl = '';
        generatedMarkdown = '';
        originalMarkdown = '';
        verificationSummary = null;
        isLoading = true;

        try {
            // Build prompt obj with all the req params
            const prompt = {
                prompt: keyPoints,
                topicHeading,
                slideDeckLength,
                detailLevel,
                textTone,
                show_annotations: showAnnotations
            };

            const response = await generateSlides(prompt);
            generatedMarkdown = response.markdown;
            originalMarkdown = response.original_markdown || '';
            verificationSummary = response.verification_summary || null;
        } catch (err) {
            error = err.message || 'Failed to generate slides';
        } finally {
            isLoading = false;
        }
    }

    async function exportToSlides() {
        if (!generatedMarkdown) {
            error = "Please generate slides first before exporting";
            return;
        }

        error = '';
        exportSuccess = null;
        exportedSlideUrl = '';
        isExporting = true;

        try {
            const result = await exportToGoogleSlides({
                    markdown: generatedMarkdown,
                    title: topicHeading || 'Generated Slide Deck'
            });

            if (result.status === 'success') {
                exportSuccess = true;
                exportedSlideUrl = result.presentation_url;
                // Open presentation in new tab
                window.open(result.presentation_url, '_blank');
            } else {
                exportSuccess = false;
                error = result.message || 'Failed to export to Google Slides';
            }
        } catch (err) {
            exportSuccess = false;
            error = err.message || 'Failed to export to Google Slides';
            console.error('Export error: ', err);
        } finally {
            isExporting = false;
            console.log("Export process completed, button state reset");
        }
    }

    // need to render differently for annotations
    function customRenderer() {
        const renderer = new marked.Renderer();

        // going to store original paragraph renderer
        const originalParagraph = renderer.paragraph.bind(renderer);

        // going to override the paragraph renderer to handle the custom annotations
        renderer.paragraph = (text) => {
            return originalParagraph(text); // custom will be applied via CSS
        };

        return renderer;
    }

    // going to configure annotations with the custom renderer
    marked.setOptions({
       renderer: customRenderer(),
       gfm: true,
       breaks: true
    });

    // $ means it's a reactive statement
    $: parsedMarkdown = generatedMarkdown ? marked(generatedMarkdown) : ''; // converting markdown to HTML using marked()

    function toggleAnnotations() {
        showAnnotations = !showAnnotations;
        handleSubmit();
    }
</script>

<div class="prompt-form">
    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="topicHeading">Topic</label>
            <input
                id="topicHeading"
                type="text"
                bind:value={topicHeading}
                placeholder="Enter the main topic of the slide deck"
                required
            />
        </div>

        <div class="form-group">
            <label for="keyPoints">Key Points/Requirements</label>
            <textarea
                    bind:value={keyPoints}
                    placeholder="Enter your slide deck requirements..."
                    rows="4"
                    required
            ></textarea>
        </div>

        <div class="requirement-selection">
            <div class="option-group">
                <h3>Slide Deck Length</h3>
                <div class="card-options">
                    {#each options.slideDeckLength as option}
                        <div
                            class="option-card"
                            class:selected={slideDeckLength === option.value}
                            on:click={() => slideDeckLength = option.value}
                        >
                            <div class="card-header">{option.label}</div>
                            <div class="card-description">{option.description}</div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="option-group">
                <h3>Detail Level</h3>
                <div class="card-options">
                    {#each options.detailLevel as option}
                        <div
                                class="option-card"
                                class:selected={detailLevel === option.value}
                                on:click={() => detailLevel = option.value}
                        >
                            <div class="card-header">{option.label}</div>
                            <div class="card-description">{option.description}</div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="option-group">
                <h3>Text Tone</h3>
                <div class="card-options">
                    {#each options.textTone as option}
                        <div
                                class="option-card"
                                class:selected={textTone === option.value}
                                on:click={() => textTone = option.value}
                        >
                            <div class="card-header">{option.label}</div>
                            <div class="card-description">{option.description}</div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>



        <button class="submit-btn" type="submit" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Slides with Gemma2'}
        </button>
    </form>

    {#if error}
        <div class="error">{error}</div>
    {/if}

    {#if generatedMarkdown}
        <div class="button-group">
            <button class="export-btn" on:click={exportToSlides} disabled={isExporting}>
                {isExporting ? 'Exporting...' : 'Export to Google Slides'}
            </button>

            {#if isExporting}
                <button
                        class="reset-btn"
                        on:click={() => { isExporting = false; error = ''; }}>
                    Reset Export
                </button>
            {/if}

            <button class="toggle-btn" on:click={toggleAnnotations}>
                {showAnnotations ? 'Hide Annotations' : 'Show Annotations'}
            </button>
        </div>

        {#if exportSuccess === true}
            <div class="success-message">
                Successfully exported to Google Slides!
                <a href={exportedSlideUrl} target="_blank" rel="noopener noreferrer">View Presentation</a>
            </div>
        {/if}

        {#if error}
            <div class="error">{error}</div>
        {/if}

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

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
    }

    input[type="text"] {
        width: 100%;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    textarea {
        width: 100%;
        margin-bottom: 10px;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-height: 120px;
    }

    .requirement-selection {
        margin: 25px 0;
    }

   .option-group {
       margin-bottom: 20px;
   }

   .option-group h3 {
       margin-bottom: 10px;
       font-size: 16px;
       font-weight: 500;
   }

   .card-options {
       display: flex;
       gap: 10px;
       flex-wrap: wrap; /* Allows flex items to wrap onto multiple lines*/
   }

   .option-card {
       flex: 1;
       min-width: 100px;
       padding: 12px;
       border: 1px solid #ddd;
       border-radius: 4px;
       cursor: pointer;
       transition: all 0.2s ease;
       background-color: #f9f9f9;
   }

   .option-card:hover {
       border-color: #aaa;
       background-color: #f5f5f5;
   }

   .option-card.selected {
       border-color: #3273dc;
       background-color: #eef3fc;
       box-shadow: 0 0 0 1px #3273dc;
   }

    .card-header {
        font-weight: 500;
        margin-bottom: 5px;
    }

    .card-description {
        font-size: 13px;
        color: #666;
    }

    .submit-btn {
        width: 100%;
        padding: 12px;
        margin-top: 10px;
        background-color: #3273dc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }

    .submit-btn:hover:not(:disabled) {
        background-color: #2366c7;
    }

    .submit-btn:disabled {
        background-color: #a0a0a0;
        cursor: not-allowed;
    }

    .reset-btn {
        padding: 5px 10px;
        background-color: #ff9800;
        color: white;
        border: none;
        border-radius: 4px;
        margin-left: 10px;
        cursor: pointer;
    }

    .reset-btn:hover {
        background-color: #e68a00;
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