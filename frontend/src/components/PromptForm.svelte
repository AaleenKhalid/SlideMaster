<script>
    import { generateSlides } from '$lib/api.js';
    import { marked } from 'marked';
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    let prompt = '';
    let generatedMarkdown = '';
    let error = '';
    let isLoading = false;
    let slideDeckLength = 'moderate';
    let detailLevel = 'detailed';
    let textTone = 'formal';
    let topicHeading = '';
    let keyPoints = ''; // TODO - might need to update structure

    // Option Settings
    const options = {
        slideDeckLength: [
            { value: '10-15', label: 'Short (10 -15 slides)' },
            { value: '15-35', label: 'Moderate (15 - 35 slides)' },
            { value: '35-50', label: 'Long (35 - 50 slides)' },
        ],

        detailLevel: [
            { value: 'simple', label: 'Simple' },
            { value: 'detailed', label: 'Detailed' },
        ],

        textTone: [
            { value: 'formal', label: 'Formal' },
            { value: 'casual', label: 'Casual' },
            { value: 'academic', label: 'Academic' },
        ]
    };

    // Have active option section
    let activeOption = 'slideDeckLength';

    function setActiveOption(option) {
        activeOption = option;
    }

    function selectOption(setting, value) {
        if (setting === 'slideDeckLength') slideDeckLength = value;
        if (setting === 'detailLevel') detailLevel = value;
        if (setting === 'textTone') textTone = textTone;
    }

    function getSelectedLabel(setting) {
        const selected = options[setting].find(opt =>
            opt.value === (setting === 'slideDeckLength') ? slideDeckLength : setting === 'detailLevel' ? detailLevel : textTone);

        return selected ? selected.label : '';
    }


    async function handleSubmit() {
        error = '';
        generatedMarkdown = '';
        isLoading = true;

        try {

            prompt = 'Topic heading will be: ' + topicHeading + '\n' +
                'Key Points you need to cover are: ' + keyPoints + '\n' +
                'There should be ' + slideDeckLength + ' slides.' + '\n' +
                'The content should have a ' + textTone + ' tone' + '\n' +
                'The content should be ' + detailLevel;

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
                    rows="5"
                    required
            ></textarea>
        </div>

        <div class="carousel-container">
            <div class="tabs">
                <button
                        type="button"
                        class:active={activeOption === 'slideDeckLength'}
                        on:click={() => setActiveOption('slideDeckLength')}
                >
                    Length: {getSelectedLabel('slideDeckLength')}
                </button>
                <button
                        type="button"
                        class:active={activeOption === 'detailLevel'}
                        on:click={() => setActiveOption('detailLevel')}
                >
                    Detail: {getSelectedLabel('detailLevel')}
                </button>
                <button
                        type="button"
                        class:active={activeOption === 'textTone'}
                        on:click={() => setActiveOption('textTone')}
                >
                    Tone: {getSelectedLabel('textTone')}
                </button>
            </div>

            <div class="carousel-options">
                {#if activeOption === 'slideDeckLength'}
                    <div transition:slide={{ duration: 300, easing: quintOut }} class="option-container">
                        {#each options.slideDeckLength as option}
                            <button
                                    type="button"
                                    class:selected={slideDeckLength === option.value}
                                    on:click={() => selectOption('slideDeckLength', option.value)}
                            >
                                {option.label}
                            </button>
                        {/each}
                    </div>
                {/if}

                {#if activeOption === 'detailLevel'}
                    <div transition:slide={{ duration: 300, easing: quintOut }} class="option-container">
                        {#each options.detailLevel as option}
                            <button
                                    type="button"
                                    class:selected={detailLevel === option.value}
                                    on:click={() => selectOption('detailLevel', option.value)}
                            >
                                {option.label}
                            </button>
                        {/each}
                    </div>
                {/if}

                {#if activeOption === 'textTone'}
                    <div transition:slide={{ duration: 300, easing: quintOut }} class="option-container">
                        {#each options.textTone as option}
                            <button
                                    type="button"
                                    class:selected={textTone === option.value}
                                    on:click={() => selectOption('textTone', option.value)}
                            >
                                {option.label}
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>



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

    .carousel-container {
        margin: 20px 0;
        border: 1px solid #eaeaea;
        border-radius: 8px;
        overflow: hidden;
    }

    .tabs {
        display: flex;
        background-color: #f5f5f5;
        border-bottom: 1px solid #eaeaea;
    }

    .tabs button {
        flex: 1;
        padding: 10px;
        background: none;
        border: none;
        cursor: pointer;
        font-weight: 500;
        color: #555;
        transition: background-color 0.2s;
    }

    .tabs button.active {
        background-color: #fff;
        color: #3273dc;
        border-bottom: 2px solid #3273dc;
    }

    .option-container {
        display: flex;
        padding: 15px;
        justify-content: center;
        gap: 10px;
        background-color: white;
    }

    .option-container button {
        padding: 8px 12px;
        background: #f5f7fa;
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .option-container button.selected {
        background-color: #3273dc;
        color: white;
        border-color: #3273dc;
    }

    .option-container button:hover:not(.selected) {
        background-color: #e8e8e8;
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