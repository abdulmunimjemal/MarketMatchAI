/**
 * RAG-specific JavaScript functionality
 * Handles querying, document processing, and visualization
 */

/**
 * Process a query against the RAG system
 * @param {string} queryText - The query text
 * @param {function} successCallback - Callback function for successful query
 * @param {function} errorCallback - Callback function for query errors
 */
function processRagQuery(queryText, successCallback, errorCallback) {
    if (!queryText || queryText.trim() === '') {
        if (errorCallback) errorCallback('Query text cannot be empty');
        return;
    }
    
    // Make API call to query endpoint
    axios.post('/api/query', {
        query: queryText
    })
    .then(response => {
        if (response.data.success) {
            if (successCallback) successCallback(response.data);
        } else {
            if (errorCallback) errorCallback(response.data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error processing query:', error);
        if (errorCallback) {
            const errorMessage = error.response?.data?.error || error.message || 'Error processing query';
            errorCallback(errorMessage);
        }
    });
}

/**
 * Upload a document to the RAG system
 * @param {File} file - The file to upload
 * @param {function} progressCallback - Callback for upload progress
 * @param {function} successCallback - Callback for successful upload
 * @param {function} errorCallback - Callback for upload errors
 */
function uploadDocument(file, progressCallback, successCallback, errorCallback) {
    if (!file) {
        if (errorCallback) errorCallback('No file provided');
        return;
    }
    
    const formData = new FormData();
    formData.append('document', file);
    
    axios.post('/api/documents/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
            if (progressCallback) {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                progressCallback(percentCompleted);
            }
        }
    })
    .then(response => {
        if (response.data.success) {
            if (successCallback) successCallback(response.data);
        } else {
            if (errorCallback) errorCallback(response.data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error uploading document:', error);
        if (errorCallback) {
            const errorMessage = error.response?.data?.error || error.message || 'Error uploading document';
            errorCallback(errorMessage);
        }
    });
}

/**
 * Fetch documents from the RAG system
 * @param {function} successCallback - Callback for successful retrieval
 * @param {function} errorCallback - Callback for retrieval errors
 */
function fetchDocuments(successCallback, errorCallback) {
    axios.get('/api/documents')
    .then(response => {
        if (response.data.success) {
            if (successCallback) successCallback(response.data.documents);
        } else {
            if (errorCallback) errorCallback(response.data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error fetching documents:', error);
        if (errorCallback) {
            const errorMessage = error.response?.data?.error || error.message || 'Error fetching documents';
            errorCallback(errorMessage);
        }
    });
}

/**
 * Fetch document details from the RAG system
 * @param {number} documentId - ID of the document to fetch
 * @param {function} successCallback - Callback for successful retrieval
 * @param {function} errorCallback - Callback for retrieval errors
 */
function fetchDocumentDetails(documentId, successCallback, errorCallback) {
    if (!documentId) {
        if (errorCallback) errorCallback('No document ID provided');
        return;
    }
    
    axios.get(`/api/documents/${documentId}`)
    .then(response => {
        if (response.data.success) {
            if (successCallback) successCallback(response.data.document);
        } else {
            if (errorCallback) errorCallback(response.data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error fetching document details:', error);
        if (errorCallback) {
            const errorMessage = error.response?.data?.error || error.message || 'Error fetching document details';
            errorCallback(errorMessage);
        }
    });
}

/**
 * Fetch recent queries from the RAG system
 * @param {function} successCallback - Callback for successful retrieval
 * @param {function} errorCallback - Callback for retrieval errors
 * @param {number} limit - Maximum number of queries to fetch
 */
function fetchRecentQueries(successCallback, errorCallback, limit = 10) {
    axios.get('/api/queries')
    .then(response => {
        if (response.data.success) {
            if (successCallback) successCallback(response.data.queries);
        } else {
            if (errorCallback) errorCallback(response.data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error fetching recent queries:', error);
        if (errorCallback) {
            const errorMessage = error.response?.data?.error || error.message || 'Error fetching recent queries';
            errorCallback(errorMessage);
        }
    });
}

/**
 * Create a visualization of document relevance to a query
 * @param {Array} sources - Array of source objects with relevance scores
 * @param {string} containerId - ID of container element for the chart
 */
function createRelevanceChart(sources, containerId) {
    if (!sources || !sources.length || !containerId) {
        console.error('Missing data for relevance chart');
        return;
    }
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Container element not found:', containerId);
        return;
    }
    
    // Prepare data for chart
    const labels = sources.map(source => source.document_title);
    const scores = sources.map(source => source.relevance_score * 100); // Convert to percentage
    
    // Create chart
    const ctx = container.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relevance Score (%)',
                data: scores,
                backgroundColor: '#4285F4',
                borderColor: '#1967D2',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Relevance: ${context.raw.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Highlight matching text in source documents
 * @param {string} sourceText - The source document text
 * @param {string} queryText - The query text to highlight matches for
 * @return {string} HTML with highlighted matches
 */
function highlightMatches(sourceText, queryText) {
    if (!sourceText || !queryText) return sourceText;
    
    // Simple word-based highlighting
    const queryWords = queryText.toLowerCase().split(/\s+/).filter(word => word.length > 3);
    let highlightedText = sourceText;
    
    queryWords.forEach(word => {
        const regex = new RegExp(`(${word})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
    });
    
    return highlightedText;
}
