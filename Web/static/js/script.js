document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ script.js loaded");
  
    const form = document.getElementById("transcribe-form");
    const resultDiv = document.getElementById("transcript-result");
  
    if (!form || !resultDiv) {
      console.error("❌ Form or result container not found in HTML");
      return;
    }
  
    let pollingInterval = null;
  
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      console.log("🟢 Form submitted");
  
      const formData = new FormData(form);
  
      resultDiv.innerHTML = `
        <div class="progress my-3">
          <div class="progress-bar progress-bar-striped progress-bar-animated"
               role="progressbar" style="width: 0%" id="progress-bar">0%</div>
        </div>
        <p class="text-muted">Transcribing... please wait.</p>
      `;
  
      console.log("📤 Sending form data to /transcribe");
  
      fetch("/transcribe", {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      })
      .then(response => {
        console.log("🧪 Raw fetch response:", response);
        return response.json();
      })
      .then(data => {
        console.log("📦 Transcribe response received:", data);
  
        if (data.error) {
          console.error("❌ Transcribe error:", data.error);
          resultDiv.innerHTML = `<p class="text-danger">${data.error}</p>`;
          return;
        }
  
        const jobId = data.job_id;
        if (!jobId) {
          console.error("❌ No job ID returned from /transcribe");
          resultDiv.innerHTML = `<p class="text-danger">No job ID received</p>`;
          return;
        }
  
        console.log("🚀 Polling started for job ID:", jobId);
  
        // Start polling for progress
        pollingInterval = setInterval(() => {
          console.log("🔁 Polling /job/progress/" + jobId);
  
          fetch(`/job/progress/${jobId}`)
            .then(res => res.json())
            .then(progressData => {
              console.log("📊 Progress response:", progressData);
  
              if (progressData.progress !== undefined) {
                const percent = progressData.progress;
                const progressBar = document.getElementById("progress-bar");
  
                if (progressBar) {
                  progressBar.style.width = `${percent}%`;
                  progressBar.innerText = `${percent}%`;
                }
  
                if (percent >= 100) {
                  console.log("✅ Transcription complete, fetching final result");
                  clearInterval(pollingInterval);
  
                  console.log("🧪 Hitting /job/result to get transcript...");
                  fetch(`/job/result/${jobId}`)
                    .then(res => res.json())
                    .then(resultData => {
                      console.log("📥 Final result received:", resultData);
  
                      if (resultData.error) {
                        console.warn("⚠️ Result not ready:", resultData.error);
                        resultDiv.innerHTML = `<p class="text-warning">${resultData.error}</p>`;
                      } else {
                        resultDiv.innerHTML = `
                          <h4>Transcript Preview</h4>
                          <pre>${resultData.transcript}</pre>
                          <div class="d-flex gap-3 mt-3">
                            <a href="/static/output/${resultData.download_txt}" class="btn btn-primary">Download .txt</a>
                            <a href="/static/output/${resultData.download_srt}" class="btn btn-secondary">Download .srt</a>
                          </div>
                        `;
                      }
                    })
                    .catch(err => {
                      console.error("❌ Error fetching transcript result:", err);
                    });
                }
              } else {
                console.warn("⚠️ Progress is undefined:", progressData);
              }
            })
            .catch(err => {
              console.error("❌ Error while polling progress:", err);
              clearInterval(pollingInterval);
            });
        }, 4000); 
      })
      .catch((error) => {
        console.error("❌ Fetch error during form submit:", error);
        clearInterval(pollingInterval);
        resultDiv.innerHTML = `<p class="text-danger">Something went wrong: ${error}</p>`;
      });
    });
  });
  