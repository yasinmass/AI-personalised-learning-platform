document.addEventListener('DOMContentLoaded', function() {
    // Only run on the CourseVideo admin pages
    const courseSelect = document.getElementById('id_course');
    const topicInput = document.getElementById('id_topic');
    if (!courseSelect || !topicInput) return;

    // Utility to replace topic input with a select populated with topics
    function buildOptionsIntoSelect(select, topics, currentValue) {
        // clear existing options
        while (select.firstChild) select.removeChild(select.firstChild);

        // add placeholder
        const emptyOpt = document.createElement('option');
        emptyOpt.value = '';
        emptyOpt.text = '— select topic —';
        select.appendChild(emptyOpt);

        if (!topics || topics.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.text = 'No LLM topics found — generate roadmap to populate';
            opt.disabled = true;
            select.appendChild(opt);
        } else {
            topics.forEach(function(t) {
                const opt = document.createElement('option');
                opt.value = t;
                opt.text = t;
                select.appendChild(opt);
            });
        }

        // preserve custom current value if provided
        if (currentValue) {
            let found = Array.from(select.options).some(o => o.value === currentValue);
            if (!found) {
                const custom = document.createElement('option');
                custom.value = currentValue;
                custom.text = currentValue + ' (custom)';
                select.appendChild(custom);
            }
            select.value = currentValue;
        }
    }

    function ensureTopicSelect(topics, currentValue) {
        const existing = document.getElementById('id_topic');
        if (existing && existing.tagName === 'SELECT') {
            buildOptionsIntoSelect(existing, topics, currentValue);
            return existing;
        }

        // create a select element
        const select = document.createElement('select');
        select.id = 'id_topic';
        select.name = 'topic';
        select.className = 'vTextField form-control';
        buildOptionsIntoSelect(select, topics, currentValue);

        // replace whatever element currently has id_topic
        const cur = document.getElementById('id_topic');
        if (cur && cur.parentNode) {
            cur.parentNode.replaceChild(select, cur);
        }
        return select;
    }

    // Fetch topics for a course and update the topic field
    function fetchAndPopulate(courseId) {
        if (!courseId) return;
        const url = `/admin/courses/coursevideo/fetch-topics/?course_id=${courseId}`;
        fetch(url).then(function(resp) {
            if (!resp.ok) return [];
            return resp.json();
        }).then(function(data) {
            if (!data) return;
            const topics = data.topics || [];
            const currentVal = (document.getElementById('id_topic') && document.getElementById('id_topic').value) || '';
            // If topic input has already been replaced by a select, keep reference
            const existing = document.getElementById('id_topic');
            if (existing && existing.tagName === 'SELECT') {
                // rebuild options
                const sel = replaceTopicWithSelect(topics, currentVal);
                return;
            }
            replaceTopicWithSelect(topics, currentVal);
        }).catch(function(err) {
            // Fail silently - keep original input
            console.warn('Failed to fetch topics for course:', err);
        });
    }

    // Initial populate based on current course value (useful when editing)
    if (courseSelect.value) {
        fetchAndPopulate(courseSelect.value);
    }

    // When course changes, fetch topics
    courseSelect.addEventListener('change', function(e) {
        const val = e.target.value;
        fetchAndPopulate(val);
    });

});
