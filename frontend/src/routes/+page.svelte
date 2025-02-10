<script>
    import PromptForm from '../components/PromptForm.svelte';
</script>

<main class="container">
    <header>
        <h1>AI Slide Deck Generator</h1>
        <p class="subtitle">Enter your requirements and let AI create your slide deck content</p>
    </header>

    <section class="form-section">
        <PromptForm />
    </section>
</main>

<style>
    .container {
        min-height: 100vh;
        padding: 2rem;
        background-color: #f5f7fa;
    }

    header {
        text-align: center;
        margin-bottom: 2rem;
    }

    h1 {
        color: #2d3748;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #4a5568;
        font-size: 1.1rem;
        margin-top: 0;
    }

    .form-section {
        margin: 0 auto;
        max-width: 1000px;
    }


    /* Responsive design */
    @media (max-width: 768px) {
        .container {
            padding: 1rem;
        }

        h1 {
            font-size: 2rem;
        }

        .subtitle {
            font-size: 1rem;
        }
    }
</style>