/**
 * bgm_handler.js
 * Handles persistent background music state across pages using sessionStorage.
 * Includes improved autoplay handling and user feedback.
 */

(function() {
    // Ensure this runs after the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupBGM);
    } else {
        setupBGM();
    }

    function setupBGM() {
        const bgm = document.getElementById('bgm');
        const toggle = document.getElementById('bgmToggle');

        // Exit if essential elements aren't found on this page
        if (!bgm || !toggle) {
            // console.log("BGM elements not found on this page.");
            return;
        }

        const storageKeyMuted = 'bgmMuted'; // Key for storing muted state in sessionStorage
        const storageKeyPos = 'bgmPos';     // Key for storing playback position

        // --- Restore Session State ---
        let muted = sessionStorage.getItem(storageKeyMuted) === 'true';
        let position = parseFloat(sessionStorage.getItem(storageKeyPos) || '0');

        bgm.volume = 0.7; // Set default volume (adjust as needed)
        bgm.muted = muted; // Set muted state BEFORE setting time
        bgm.currentTime = isFinite(position) ? position : 0;


        console.log(`BGM Handler: Initialized on ${window.location.pathname}. Muted: ${bgm.muted}, Position: ${bgm.currentTime}`);

        // --- UI Update Function ---
        function setLabel() {
            if (toggle) { // Check if toggle exists before setting text
                 toggle.textContent = bgm.muted ? 'PLAY' : 'MUTE';
            }
        }
        setLabel(); // Set initial button text

        // --- Autoplay Attempt Function (Used for initial load & bfcache) ---
        // Added user feedback and more robust interaction handling
        function tryPlay(isUserInitiated = false) {
             console.log(`BGM Handler: tryPlay called. isUserInitiated: ${isUserInitiated}. Muted: ${bgm.muted}, Paused: ${bgm.paused}`);

             // Only attempt play if not muted and paused
             if (!bgm.muted && bgm.paused) {
                 // Check if the element is ready and has metadata loaded
                  if (bgm.readyState < 2 && bgm.networkState !== 3) {
                      console.log("BGM Handler: Audio not ready, waiting for canplay event.");
                      bgm.addEventListener('canplay', () => {
                          console.log("BGM Handler: canplay event fired, attempting play.");
                          tryPlay(isUserInitiated); // Retry play once audio is ready
                      }, { once: true });
                      return; // Exit for now, will retry on canplay
                  }

                 console.log("BGM Handler: Attempting to play BGM.");
                 const playPromise = bgm.play();
                 if (playPromise !== undefined) {
                     playPromise.then(() => {
                         console.log("BGM Handler: Play successful.");
                         // Hide any autoplay blocked messages if they exist
                         hideAutoplayBlockedMessage();
                     }).catch((error) => {
                         console.log("BGM Handler: Autoplay blocked by browser:", error);
                         if (!isUserInitiated) {
                             // Show message and add interaction listeners only if not already user-initiated
                             showAutoplayBlockedMessage();
                             const resumeOnInteraction = () => {
                                 console.log("BGM Handler: User gesture detected, calling tryPlay(true).");
                                 tryPlay(true); // Call again, marking as user-initiated
                                 // Remove listeners after the first interaction
                                 window.removeEventListener('click', resumeOnInteraction, { once: true });
                                 window.removeEventListener('keydown', resumeOnInteraction, { once: true });
                                 // Hide the message
                                 hideAutoplayBlockedMessage();
                             };
                             // Ensure listeners are not added multiple times
                             window.removeEventListener('click', resumeOnInteraction, { once: true });
                             window.removeEventListener('keydown', resumeOnInteraction, { once: true });
                             window.addEventListener('click', resumeOnInteraction, { once: true });
                             window.addEventListener('keydown', resumeOnInteraction, { once: true });
                             console.log("BGM Handler: Added interaction listeners for blocked autoplay.");
                         } else {
                             console.log("BGM Handler: Play failed even after user interaction.");
                             // You might want to show a persistent error message here
                         }
                     });
                 }
             } else if (!bgm.muted && !bgm.paused) {
                 console.log("BGM Handler: tryPlay called. BGM already playing.");
                 // Hide any autoplay blocked messages if music is now playing
                 hideAutoplayBlockedMessage();
             } else {
                 console.log("BGM Handler: tryPlay called. BGM is muted.");
                 // If muted, ensure it's paused and hide any messages
                 bgm.pause();
                 hideAutoplayBlockedMessage();
             }
         }

        // --- Autoplay Blocked Message UI ---
        function showAutoplayBlockedMessage() {
            let messageElement = document.getElementById('autoplayBlockedMessage');
            if (!messageElement) {
                messageElement = document.createElement('div');
                messageElement.id = 'autoplayBlockedMessage';
                Object.assign(messageElement.style, {
                    position: 'fixed',
                    bottom: '50px', // Position above the mute button
                    right: '18px',
                    background: 'rgba(255, 0, 0, 0.8)',
                    color: 'white',
                    padding: '8px 12px',
                    borderRadius: '4px',
                    fontFamily: 'Share Tech Mono, monospace',
                    fontSize: '0.8em',
                    zIndex: '10000',
                    display: 'block' // Ensure it's visible
                });
                document.body.appendChild(messageElement);
            }
            messageElement.textContent = 'Click anywhere or press a key to enable music.';
            messageElement.style.display = 'block';
            console.log("BGM Handler: Showing autoplay blocked message.");
        }

        function hideAutoplayBlockedMessage() {
            const messageElement = document.getElementById('autoplayBlockedMessage');
            if (messageElement) {
                messageElement.style.display = 'none';
                console.log("BGM Handler: Hiding autoplay blocked message.");
            }
        }


        // --- Initial Play Logic ---
        // Determine if BGM should attempt to play on page load.
        // It should play unless it's the very first boot sequence on the home page.
        const isHomePage = document.getElementById('boot') !== null;
        const isBootComplete = document.body.classList.contains('boot-complete');
        const isIdentifyPage = window.location.pathname.includes('/identify'); // Identify page
        const isManifestoPage = window.location.pathname.includes('/manifesto'); // Manifesto page

        // BGM should attempt to play if:
        // 1. It's NOT the home page, OR
        // 2. It IS the home page AND the boot sequence is complete, OR
        // 3. It's a page where BGM is expected (not identify/manifesto unless specifically added there)
        //    (Assuming BGM is desired on Quest, Snake Quest, Armory, Snake Intro pages)

        // Let's simplify: BGM attempts to play on any page load *except* the initial state of the home page before boot.
        // It also shouldn't play on pages where the audio element isn't present, which the initial check handles.

        // If on the home page and boot is NOT complete, assign tryPlay to a global variable
        // that the boot sequence script can call once boot is done.
        if (isHomePage && !isBootComplete) {
             console.log("BGM Handler: On Home page, boot not complete. Assigning tryPlay to window.tryPlayBGM.");
             window.tryPlayBGM = tryPlay; // Make it accessible
        } else {
            // On any other page, or home page after boot, attempt play immediately
             console.log(`BGM Handler: Page loaded. IsHome: ${isHomePage}, BootComplete: ${isBootComplete}. Calling tryPlay.`);
             tryPlay();
        }


        // --- Toggle Button Click Handler ---
        toggle.addEventListener('click', () => {
            // 1. Toggle the muted state directly on the element
            bgm.muted = !bgm.muted;
            console.log(`BGM Handler: Toggle clicked. New muted state: ${bgm.muted}`);

            // 2. Save the new state
            sessionStorage.setItem(storageKeyMuted, bgm.muted);

            // 3. Update the button label
            setLabel();

            // 4. If unmuting, attempt to play. If muting, pause.
            if (!bgm.muted) {
                 console.log("BGM Handler: Unmuting, attempting play.");
                 tryPlay(true); // Mark as user-initiated
            } else {
                 console.log("BGM Handler: Muting, pausing BGM.");
                 bgm.pause();
                 // Hide the autoplay blocked message if it was showing
                 hideAutoplayBlockedMessage();
            }
        });


        // --- Save Playback Position Periodically ---
        let saveTimer = setInterval(() => {
            if (bgm && !bgm.paused && !bgm.muted) {
                if (isFinite(bgm.currentTime) && bgm.currentTime > 0) {
                    sessionStorage.setItem(storageKeyPos, bgm.currentTime);
                }
            }
        }, 3000);

        // --- Save Position Before Unload ---
        window.addEventListener('beforeunload', () => {
            if (bgm && !bgm.paused && !bgm.muted) {
                 if (isFinite(bgm.currentTime) && bgm.currentTime > 0) {
                    sessionStorage.setItem(storageKeyPos, bgm.currentTime);
                 }
            }
            // Clear the interval when leaving the page
            clearInterval(saveTimer);
            saveTimer = null; // Set to null after clearing
        });

        // --- Handle Browser Back/Forward Cache (bfcache) ---
        window.addEventListener('pageshow', (event) => {
            console.log(`BGM Handler: pageshow event fired. Persisted: ${event.persisted}`);

            // Always re-sync state from sessionStorage on pageshow
            muted = sessionStorage.getItem(storageKeyMuted) === 'true';
            position = parseFloat(sessionStorage.getItem(storageKeyPos) || '0');
            bgm.muted = muted; // Apply muted state first
            // Restore position, but only if it's a valid number
            bgm.currentTime = isFinite(position) ? position : 0;

            console.log(`BGM Handler: Restored BGM state on pageshow. Muted: ${bgm.muted}, Position: ${bgm.currentTime}`);
            setLabel(); // Update button label

            // If the page was restored from bfcache AND music should be playing, attempt play
            // Music should be playing if not muted AND (it's not the home page OR boot is complete)
            const isBooted = (!isHomePage || document.body.classList.contains('boot-complete'));
            const shouldBePlaying = isBooted && !bgm.muted;

            if (event.persisted && shouldBePlaying) {
                // Use setTimeout to slightly delay the play attempt to avoid potential race conditions
                setTimeout(() => {
                    console.log("BGM Handler: Page restored from bfcache, attempting delayed play.");
                    // Pass true because bfcache restore implies prior user interaction
                    tryPlay(true);
                }, 100); // 100ms delay (adjust if needed)
            } else if (event.persisted) {
                 console.log(`BGM Handler: Page restored from bfcache. ShouldBePlaying: ${shouldBePlaying}. No delayed play attempt.`);
                 // If restored from bfcache but shouldn't be playing (e.g., was muted), ensure it's paused
                 if (bgm.muted || !isBooted) {
                      bgm.pause();
                 }
            } else {
                // Not from bfcache, normal page load. tryPlay was already called or assigned.
                console.log("BGM Handler: Page loaded normally (not from bfcache).");
            }


            // Ensure save timer is running if needed
            if (!bgm.paused && !bgm.muted && saveTimer === null) {
                saveTimer = setInterval(() => { if (bgm && isFinite(bgm.currentTime)) sessionStorage.setItem(storageKeyPos, bgm.currentTime); }, 3000);
            } else if ((bgm.paused || bgm.muted) && saveTimer !== null) {
                clearInterval(saveTimer);
                saveTimer = null;
            }
        });
    } // end setupBGM

})(); // IIFE
