<script>
    import {exportToGoogleSlides, generateSlides} from '$lib/api.js';
    import {marked} from 'marked';

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

        // // going to store original paragraph renderer
        // const originalParagraph = renderer.paragraph.bind(renderer);
        //
        // // going to override the paragraph renderer to handle the custom annotations
        // renderer.paragraph = (text) => {
        //     return originalParagraph(text); // custom will be applied via CSS
        // };

        marked.use({
            renderer: {
                // Custom handling for verification warnings in markdown
                text(text) {
                    // Style unverified statements with a yellow background and warning icon
                    const unverifiedPattern = /\*\*⚠️ \[UNVERIFIED\]:(.*?)⚠️\*\*/g;
                    return text.replace(
                        unverifiedPattern,
                        '<span class="unverified-statement" title="This statement could not be verified">$2</span>'
                    );
                }
            }
        });


        return renderer;
    }

    customRenderer(); // setting up the renderer

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


            <div class="option-group">
                <h3>Verification</h3>
                <div class="verification-toggle">
                    <label class="toggle-switch">
                        <input type="checkbox" bind:checked={showAnnotations}>
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Show fact-checking annotations</span>
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

            {#if verificationSummary}
                <div class="verification-summary">
                    <div class="verification-rate">
                        <span class="rate-label">Verification Rate:</span>
                        <div class="progress-bar">
                            <div
                                    class="progress-fill"
                                    style="width: {(verificationSummary.verification_rate || 0) * 100}%"
                            ></div>
                        </div>
                        <span class="rate-value">
                            {((verificationSummary.verification_rate || 0) * 100).toFixed(1)}%
                        </span>
                    </div>

                    <div class="stats">
                        <div class="stat">
                            <span class="stat-value">{verificationSummary.verified_statements || 0}</span>
                            <span class="stat-label">Verified</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">{verificationSummary.problematic_statements?.length || 0}</span>
                            <span class="stat-label">Unverified</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">{verificationSummary.error_statements?.length || 0}</span>
                            <span class="stat-label">Errors</span>
                        </div>
                    </div>

                    <button class="toggle-verification" on:click={toggleAnnotations}>
                        {showAnnotations ? 'Hide Verification Annotations' : 'Show Verification Annotations'}
                    </button>
                </div>
            {/if}

            <div class="markdown-content">
                {@html parsedMarkdown}
            </div>

            {#if originalMarkdown && showAnnotations}
                <div class="original-markdown">
                    <h4>Original Markdown (without annotations):</h4>
                    <div class="original-content">
                        {@html marked(originalMarkdown)}
                    </div>
                </div>
            {/if}

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

    .verification-toggle {
        display: flex;
        align-items: center;
        padding: 12px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 24px;
        margin-right: 10px;
    }

    .toggle-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 24px;
    }

    .toggle-slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }

    input:checked + .toggle-slider {
        background-color: #3273dc;
    }

    input:checked + .toggle-slider:before {
        transform: translateX(26px);
    }

    .toggle-label {
        font-size: 14px;
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

    .verification-summary {
        margin-bottom: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 6px;
        border-left: 4px solid #3273dc;
    }

    .verification-rate {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }

    .rate-label {
        min-width: 120px;
        font-weight: 500;
    }

    .progress-bar {
        flex-grow: 1;
        height: 8px;
        background-color: #eee;
        border-radius: 4px;
        margin: 0 10px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background-color: #4caf50;  /* Green for good verification */
        transition: width 0.3s ease;
    }

    /* Change color based on verification rate */
    .progress-fill[style*="width: 0%"],
    .progress-fill[style*="width: 1"],
    .progress-fill[style*="width: 2"],
    .progress-fill[style*="width: 3"] {
        background-color: #f44336;  /* Red for poor verification */
    }

    .progress-fill[style*="width: 4"],
    .progress-fill[style*="width: 5"],
    .progress-fill[style*="width: 6"] {
        background-color: #ff9800;  /* Orange for medium verification */
    }

    .rate-value {
        min-width: 50px;
        text-align: right;
        font-weight: 600;
    }

    .stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }

    .stat {
        text-align: center;
        padding: 8px 15px;
        background-color: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        flex: 1;
        margin: 0 5px;
    }

    .stat-value {
        display: block;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .stat-label {
        font-size: 12px;
        color: #666;
    }

    .toggle-verification {
        padding: 8px 15px;
        background-color: #3273dc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    }

    .toggle-verification:hover {
        background-color: #2366c7;
    }

    .markdown-content {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-bottom: 20px;
    }

    .markdown-content {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-bottom: 20px;
        line-height: 1.6;
    }

    /* Style for unverified statements */
    .unverified-statement {
        background-color: #fff3cd;
        padding: 2px 4px;
        border-radius: 3px;
        position: relative;
        border-bottom: 2px dashed #ffc107;
    }

    .unverified-statement:before {
        content: "⚠️";
        margin-right: 4px;
        font-size: 0.8em;
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