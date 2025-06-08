/* armory.js - Synced with complete-armory-js.js Slith logic
   This version includes:
   - JavaScript-based scrollbar theming fix.
   - Slith theme JavaScript effects with 30-minute interval and immediate test appearance.
   - Prevent dynamic scrollbar styling on quest pages.
   - Ensure 'boot-complete' class is added to body on non-home pages.
   - Other theme effects (Hologram, Divine Machinery, Syntax Highlighting).
*/

// Global cleanup function
function cleanupThemeElements() {
  console.log("[Cleanup] Starting cleanup...");

  // Remove any theme elements added by JS (including Slith)
  document.querySelectorAll('[data-theme-element]').forEach(element => {
    console.log("[Cleanup] Removing element:", element);
    if (element.parentNode) element.parentNode.removeChild(element);
  });

  // Clear any running intervals for JS effects (including Slith interval)
  if (window.themeIntervals && window.themeIntervals.length > 0) {
    console.log("[Cleanup] Clearing intervals:", window.themeIntervals);
    window.themeIntervals.forEach(intervalId => {
        clearInterval(intervalId);
        // Check if it was the Slith interval
        if (window.slithIntervalId && intervalId === window.slithIntervalId) {
            console.log("[Cleanup] Cleared Slith interval.");
            window.slithIntervalId = null; // Reset Slith interval tracker
        }
    });
    window.themeIntervals = []; // Clear the array
  } else {
    console.log("[Cleanup] No intervals to clear.");
  }
   // Ensure Slith interval tracker is reset if it exists outside the main array
   if (window.slithIntervalId) {
       console.warn("[Cleanup] Clearing potentially orphaned Slith interval ID.");
       clearInterval(window.slithIntervalId);
       window.slithIntervalId = null;
   }


  // Remove dynamically added scrollbar style
  const dynamicScrollbarStyle = document.getElementById('dynamic-scrollbar-style');
  if (dynamicScrollbarStyle) {
    console.log("[Cleanup] Removing dynamic scrollbar style.");
    dynamicScrollbarStyle.remove();
  }
  console.log("[Cleanup] Finished cleanup.");
}

// Function to dynamically apply scrollbar theme
function applyScrollbarTheme() {
    // Check if the current page is a quest page
    if (window.location.pathname.includes('/quest/')) {
        console.log("[Scrollbar] Skipping dynamic scrollbar theme on quest page.");
        const existingStyleElement = document.getElementById('dynamic-scrollbar-style');
        if (existingStyleElement) {
            console.log("[Scrollbar] Removing existing dynamic style on quest page.");
            existingStyleElement.remove();
        }
        return; // Exit
    }

    console.log("[Scrollbar] Attempting to apply scrollbar theme...");
    try {
        const bodyStyles = getComputedStyle(document.body);
        const neonColor = bodyStyles.getPropertyValue('--neon').trim() || '#00ff99';
        const accentColor = bodyStyles.getPropertyValue('--accent').trim() || '#ff00cc';
        const bgColor = bodyStyles.getPropertyValue('--bg').trim() || '#0b0b0b';

        console.log("[Scrollbar] Computed Colors:", { neon: neonColor, accent: accentColor, bg: bgColor });

        const scrollbarCSS = `
            /* Dynamically Applied Global Scrollbar Styles */
            ::-webkit-scrollbar { width: 10px !important; height: 10px !important; }
            ::-webkit-scrollbar-track { background: ${bgColor} !important; }
            ::-webkit-scrollbar-thumb { background: ${neonColor} !important; border-radius: 4px !important; border: 1px solid ${bgColor} !important; }
            ::-webkit-scrollbar-thumb:hover { background: ${accentColor} !important; }
            * { scrollbar-width: thin !important; scrollbar-color: ${neonColor} ${bgColor} !important; }
        `;

        const existingStyleElement = document.getElementById('dynamic-scrollbar-style');
        if (existingStyleElement) {
            console.log("[Scrollbar] Removing existing dynamic style.");
            existingStyleElement.remove();
        }

        const styleElement = document.createElement('style');
        styleElement.id = 'dynamic-scrollbar-style';
        styleElement.textContent = scrollbarCSS;
        document.head.appendChild(styleElement);
        console.log("[Scrollbar] Successfully applied dynamic scrollbar styles.");

    } catch (error) {
        console.error("[Scrollbar] Error applying scrollbar theme:", error);
    }
}


// Initialize armory features when page loads
document.addEventListener('DOMContentLoaded', function() {
  console.log("[Init] DOMContentLoaded event fired.");
  // Always clean up first
  cleanupThemeElements();

  // Initialize theme intervals array
  window.themeIntervals = [];
  window.slithIntervalId = null; // Initialize Slith interval tracker

  // Add the 'boot-complete' class to the body immediately on DOMContentLoaded,
  // but only if it's not the home page's initial state.
  if (!document.getElementById('boot')) {
      document.body.classList.add('boot-complete');
      console.log("[Armory] Added boot-complete class to body on non-home page.");
  }

  // Initialize the armory (applies theme classes)
  initArmory(); // This now fetches items and calls applyActiveItems

  // --- CRT Power-on Sound Logic ---
  // Placed after initArmory to ensure theme classes are potentially set
  const crtOnSound = document.getElementById('crtOnSound');
  const crtFlicker = document.getElementById('crtFlicker');

  if (crtOnSound && crtFlicker) {
    console.log("[Init] CRT elements found.");
    // Check if we are on a quest page and not using a theme that replaces the CRT
    if (window.location.pathname.includes('/quest/') &&
        !document.body.classList.contains('theme-divine-machinery') &&
        !document.body.classList.contains('frame-neoncrt')) {
      console.log("[Init] Adding CRT sound listener.");
      crtFlicker.addEventListener('animationstart', (event) => {
        if (event.animationName === 'crtOn') {
          console.log("[Init] CRT animation started, playing sound.");
          crtOnSound.currentTime = 0;
          crtOnSound.volume = 0.8;
          crtOnSound.play().catch(() => {
            console.log("[Init] CRT sound autoplay blocked, setting up interaction listener.");
            const resume = () => {
              console.log("[Init] Interaction detected, resuming CRT sound.");
              crtOnSound.currentTime = 0;
              crtOnSound.volume = 0.8;
              crtOnSound.play().catch(() => {});
              window.removeEventListener('click', resume);
              window.removeEventListener('keydown', resume);
            };
            window.addEventListener('click', resume, { once: true });
            window.addEventListener('keydown', resume, { once: true });
          });
        }
      });
    } else {
        console.log("[Init] CRT sound listener skipped (not quest page or theme active).");
    }
  } else {
    console.log("[Init] CRT elements not found.");
  }
  // --- End CRT Power-on Sound Logic ---

});

// Main initialization function
function initArmory() {
  console.log("[Armory] initArmory called.");
  // Fetch active items from the server
  fetch('/get_active_items')
    .then(response => {
        console.log("[Armory] Fetched active items response:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
      console.log("[Armory] Active items data:", data);
      if (data.success) {
        applyActiveItems(data.active_items); // Apply themes/effects
      } else {
          console.warn("[Armory] Fetch successful but API returned success:false.");
          applyActiveItems([]); // Apply default state (no active items)
      }
      console.log("[Armory] Body classes after fetch/applyActiveItems:", document.body.className);
    })
    .catch(error => {
      console.error('[Armory] Failed to load active items:', error);
      applyActiveItems([]); // Apply default state on error
      console.log("[Armory] Body classes after fetch error:", document.body.className);
    });
}

// Apply effects from active items
function applyActiveItems(items) {
  console.log("[Armory] applyActiveItems called with:", items);
  // First, clean up any existing theme elements and effects
  cleanupThemeElements();

  // Remove all previous armory classes from body
  const classesToRemove = Array.from(document.body.classList)
    .filter(cls => cls.startsWith('theme-') ||
                   cls.startsWith('effect-') ||
                   cls.startsWith('bg-') ||
                   cls.startsWith('frame-'));
  if (classesToRemove.length > 0) {
      console.log("[Armory] Removing classes:", classesToRemove);
      document.body.classList.remove(...classesToRemove);
  }

  // Apply new classes based on active items
  items.forEach(itemId => {
    console.log("[Armory] Processing item:", itemId);
    let classAdded = '';
    switch(itemId) {
      // Terminal themes
      case 'terminal_green': classAdded = 'theme-terminal-green'; break;
      case 'terminal_blue': classAdded = 'theme-terminal-blue'; break;
      case 'terminal_purple': classAdded = 'theme-terminal-purple'; break;
      // Effects
      case 'glitch_cursor': classAdded = 'effect-glitch-cursor'; break;
      // Backgrounds
      case 'matrix_rain': classAdded = 'bg-matrix-rain'; break;
      // Editor enhancements
      case 'syntaxhacker': enhanceSyntaxHighlighting(); break;
      // Frames
      case 'neoncrt': classAdded = 'frame-neoncrt'; break;
      // Theme packs
      case 'retrowave': classAdded = 'theme-retrowave'; break;
      // Premium themes
      case 'hologram': classAdded = 'theme-hologram'; setupHologramEffect(); break;
      case 'divine_machinery': classAdded = 'theme-divine-machinery'; setupDivineMachineryTheme(); break;
      case 'slith': classAdded = 'theme-slith'; setupSlithTheme(); break; // Calls the updated function
    }
    if (classAdded) {
        console.log(`[Armory] Adding class: ${classAdded}`);
        document.body.classList.add(classAdded);
    }
  });

  // --- Apply Scrollbar Theme ---
  // Call this *after* all body classes have been applied
  console.log("[Armory] Scheduling applyScrollbarTheme...");
  setTimeout(() => {
      applyScrollbarTheme(); // Will check path internally
  }, 0);
  // --- End Apply Scrollbar Theme ---

  console.log("[Armory] applyActiveItems finished. Current body classes:", document.body.className);
}

// Enhanced syntax highlighting (remains the same)
function enhanceSyntaxHighlighting() {
  console.log("[Effect] enhanceSyntaxHighlighting called.");
  // Check if Ace editor exists on the page
  if (typeof ace === 'undefined' || !document.getElementById('editor') && !document.getElementById('ace-wrapper')) {
      console.warn("[Effect] Ace editor not found for syntax highlighting enhancement.");
      return;
  }
  const styleElement = document.createElement('style');
  styleElement.setAttribute('data-theme-element', 'syntax');
  styleElement.textContent = `
    .ace_keyword { color: #ff5db1 !important; font-weight: bold; text-shadow: 0 0 2px rgba(255,93,177,0.4); }
    .ace_string { color: #00ffaa !important; text-shadow: 0 0 2px rgba(0,255,170,0.4); }
    .ace_numeric { color: #ffdd00 !important; text-shadow: 0 0 2px rgba(255,221,0,0.4); }
    .ace_function { color: #00aaff !important; text-shadow: 0 0 2px rgba(0,170,255,0.4); }
    .ace_comment { color: #7088a9 !important; font-style: italic; }
    .ace_keyword, .ace_string, .ace_numeric, .ace_function { transition: color 0.3s ease, text-shadow 0.3s ease; }
  `;
  const existingSyntaxStyle = document.querySelector('style[data-theme-element="syntax"]');
  if (!existingSyntaxStyle) {
      document.head.appendChild(styleElement);
      console.log("[Effect] Added syntax highlighting style.");
  } else {
      existingSyntaxStyle.textContent = styleElement.textContent;
      console.log("[Effect] Updated syntax highlighting style.");
  }
}


// Setup hologram parallax effect (remains the same)
function setupHologramEffect() {
  console.log("[Effect] setupHologramEffect called.");
  const editorContainer = document.querySelector('.editor-container');
  const editorElement = document.getElementById('ace-wrapper');
  if (!editorContainer || !editorElement) {
      console.warn("[Effect] Hologram: Editor container or ace-wrapper element not found.");
      return;
  }

  editorElement.setAttribute('data-theme-element', 'hologram');
  editorElement.dataset.originalTransform = editorElement.style.transform || '';

  const hologramMouseMoveHandler = (e) => {
    if (!document.body.classList.contains('theme-hologram')) return;
    const rect = editorContainer.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const x = (centerX - e.clientX) / 30;
    const y = (centerY - e.clientY) / 30;
    editorElement.style.transform = `translateZ(0) rotateX(${y * 0.5}deg) rotateY(${x * -0.5}deg)`;
  };
  const hologramMouseLeaveHandler = () => {
    if (!document.body.classList.contains('theme-hologram')) return;
    editorElement.style.transform = editorElement.dataset.originalTransform || 'translateZ(0) rotateX(0) rotateY(0)';
  };

  editorContainer.removeEventListener('mousemove', hologramMouseMoveHandler);
  editorContainer.removeEventListener('mouseleave', hologramMouseLeaveHandler);
  editorContainer.addEventListener('mousemove', hologramMouseMoveHandler);
  editorContainer.addEventListener('mouseleave', hologramMouseLeaveHandler);
  console.log("[Effect] Hologram listeners added to editor container.");
}


// Setup Divine Machinery theme (remains the same)
function setupDivineMachineryTheme() {
    console.log("[Effect] setupDivineMachineryTheme called.");
  // Apply specific Ace editor syntax styling if needed
  const styleElement = document.createElement('style');
  styleElement.setAttribute('data-theme-element', 'divine-machinery-syntax');
  styleElement.textContent = `
    .theme-divine-machinery .ace_keyword { color: #ff3333 !important; text-shadow: 0 0 5px rgba(255, 0, 0, 0.5); }
    .theme-divine-machinery .ace_string { color: #00ff99 !important; text-shadow: 0 0 3px rgba(0, 255, 153, 0.4); }
    .theme-divine-machinery .ace_numeric { color: #00cc77 !important; }
    .theme-divine-machinery .ace_function { color: #ff6666 !important; }
    .theme-divine-machinery .ace_comment { color: #00aa55 !important; font-style: italic; }
    .theme-divine-machinery .ace_operator { color: #eeeeee !important; }
  `;
   const existingDivineStyle = document.querySelector('style[data-theme-element="divine-machinery-syntax"]');
   if (!existingDivineStyle) {
       document.head.appendChild(styleElement);
       console.log("[Effect] Added Divine Machinery syntax style.");
   } else {
       existingDivineStyle.textContent = styleElement.textContent;
       console.log("[Effect] Updated Divine Machinery syntax style.");
   }

  const editorElement = document.querySelector('#ace-wrapper');
  if (!editorElement) {
      console.warn("[Effect] Divine Machinery: Editor element (#ace-wrapper) not found for effects.");
      return;
  }

  const createCross = () => {
      if (!document.body.classList.contains('theme-divine-machinery')) return;
      const cross = document.createElement('div');
      cross.setAttribute('data-theme-element', 'divine-machinery');
      Object.assign(cross.style, {
          position: 'absolute', width: '20px', height: '20px',
          background: 'url("/static/img/red_cross.png") center/contain no-repeat',
          opacity: '0', filter: 'drop-shadow(0 0 5px #ff0000)',
          pointerEvents: 'none', zIndex: '1', transition: 'opacity 2s ease-out'
      });
      const side = Math.floor(Math.random() * 4);
      if (side === 0) { cross.style.top = '5px'; cross.style.left = Math.random() * 90 + 5 + '%'; }
      else if (side === 1) { cross.style.right = '5px'; cross.style.top = Math.random() * 90 + 5 + '%'; }
      else if (side === 2) { cross.style.bottom = '5px'; cross.style.left = Math.random() * 90 + 5 + '%'; }
      else { cross.style.left = '5px'; cross.style.top = Math.random() * 90 + 5 + '%'; }
      editorElement.appendChild(cross);
      setTimeout(() => {
          if (!document.body.classList.contains('theme-divine-machinery')) { cross.remove(); return; }
          cross.style.opacity = '0.7';
          setTimeout(() => {
              if (!document.body.classList.contains('theme-divine-machinery')) { cross.remove(); return; }
              cross.style.opacity = '0';
              setTimeout(() => cross.remove(), 2000);
          }, 4000 + Math.random() * 3000);
      }, 500);
  };
  const createCircuitEffect = () => {
      if (!document.body.classList.contains('theme-divine-machinery')) return;
      const line = document.createElement('div');
      line.setAttribute('data-theme-element', 'divine-machinery');
      Object.assign(line.style, {
          position: 'absolute', backgroundColor: '#00ff99', opacity: '0',
          boxShadow: '0 0 5px #00ff99', pointerEvents: 'none', zIndex: '1',
          transition: 'opacity 1s ease'
      });
      const isHorizontal = Math.random() > 0.5;
      if (isHorizontal) {
          line.style.height = '1px'; line.style.width = (20 + Math.random() * 60) + '%';
          line.style.left = Math.random() * 20 + '%'; line.style.top = Math.random() * 100 + '%';
      } else {
          line.style.width = '1px'; line.style.height = (20 + Math.random() * 60) + '%';
          line.style.top = Math.random() * 20 + '%'; line.style.left = Math.random() * 100 + '%';
      }
      editorElement.appendChild(line);
      setTimeout(() => {
          if (!document.body.classList.contains('theme-divine-machinery')) { line.remove(); return; }
          line.style.opacity = '0.4';
          setTimeout(() => {
              if (!document.body.classList.contains('theme-divine-machinery')) { line.remove(); return; }
              line.style.opacity = '0';
              setTimeout(() => line.remove(), 1000);
          }, 3000 + Math.random() * 3000);
      }, 100);
  };

  if (window.themeIntervals) {
      console.log("[Effect] Divine Machinery: Clearing existing intervals.");
      window.themeIntervals.forEach(clearInterval);
      window.themeIntervals = [];
  } else {
      window.themeIntervals = [];
  }

  console.log("[Effect] Divine Machinery: Starting new intervals.");
  const crossInterval = setInterval(createCross, 40000); // Increased interval
  const circuitInterval = setInterval(createCircuitEffect, 25000); // Increased interval
  window.themeIntervals.push(crossInterval, circuitInterval);
}

// --- Setup Slith theme --- UPDATED based on complete-armory-js.js ---
function setupSlithTheme() {
  console.log("[Effect] setupSlithTheme called.");

  // Clear previous intervals before starting new ones
  if (window.themeIntervals) {
      console.log("[Effect] Slith: Clearing existing intervals.");
      window.themeIntervals.forEach(clearInterval);
      window.themeIntervals = [];
  } else {
      window.themeIntervals = [];
  }
   window.slithIntervalId = null; // Clear specific tracker

  // Function to create Slith appearance
  function createFixedSlith() {
    if (!document.body.classList.contains('theme-slith')) {
      console.log("[Effect] Slith: Theme not active, canceling appearance.");
      if (window.slithIntervalId) {
         console.log("[Effect] Slith: Clearing interval because theme is inactive.");
         clearInterval(window.slithIntervalId);
         window.slithIntervalId = null;
         const index = window.themeIntervals.indexOf(window.slithIntervalId);
         if (index > -1) window.themeIntervals.splice(index, 1);
      }
      return;
    }
    console.log("[Effect] Slith: Attempting to create Slith...");

    // --- Create Slith Element ---
    const slith = document.createElement('div');
    slith.setAttribute('data-theme-element', 'slith-theme');
    Object.assign(slith.style, {
        position: 'fixed', width: '80px', height: '80px',
        background: 'url("/static/img/slith.png") center/contain no-repeat',
        opacity: '0', zIndex: '9999', pointerEvents: 'none',
        transition: 'opacity 1s ease'
    });

    // --- Random Positioning ---
    const side = Math.floor(Math.random() * 4);
    const position = Math.random() * 60 + 20;
    switch(side) {
      case 0: slith.style.top = '20px'; slith.style.left = position + 'vw'; break;
      case 1: slith.style.right = '20px'; slith.style.top = position + 'vh'; break;
      case 2: slith.style.bottom = '20px'; slith.style.left = position + 'vw'; break;
      case 3: slith.style.left = '20px'; slith.style.top = position + 'vh'; break;
    }
    slith.style.transform = 'rotate(0deg)'; // Keep upright

    document.body.appendChild(slith);
    console.log("[Effect] Slith: Element created and added to DOM");

    // --- Fade In Slith ---
    setTimeout(() => { slith.style.opacity = '1'; }, 100);

    // --- Create Speech Bubble ---
    const bubble = document.createElement('div');
    bubble.setAttribute('data-theme-element', 'slith-theme');
    Object.assign(bubble.style, {
        position: 'fixed', padding: '8px 12px',
        background: 'rgba(255, 255, 255, 0.9)', color: '#000',
        borderRadius: '15px', fontSize: '12px',
        fontFamily: 'Share Tech Mono, monospace',
        boxShadow: '0 0 5px rgba(255, 221, 0, 0.5)',
        zIndex: '10000', pointerEvents: 'none', opacity: '0',
        transition: 'opacity 1s ease', maxWidth: '200px'
    });

    // --- Random Messages ---
    const messages = [ "Hacking the mainframe, one hisss at a time!", "Even the corporationsss fear my code!", "The net is full of sssnakes like me...", "Bypasssing firewalls is my specialty!", "In cybersspace, no one can hear you hisss!", "This node is under my ssscales now!", "Your data belongsss to me!", "I ssslither through the digital darknesss...", "Encrypting my trail, can't trace thisss!", "Sssome call me a bug, but I'm a feature!", "Firewall? More like a speed bump!", "Ssscaling the network one packet at a time.", "Fangsss for the access codes!", "My venom is pure binary!", "I've got ssscales in the system!", "Digital predator, virtual venom!", "Root accesss? Already got it!", "Coiling around your security measuresss...", "All your base are belong to sssnek!", "Cracking passwordsss while you sleep.", "This connection isss now poisoned!", "Injecting my code into your systemsss...", "Sssnaking through your defense layers.", "My tongue flicks at your encryption keys!", "I shed my skin, but never my digital trail.", "Venomous payload: delivered!", "No antiviruss can detect my patterns!", "Cold-blooded hacker in a warm network.", "Ssslithering past your security protocols.", "Administrator privilege: sssseized!", "My fangs pierce your data ssstructures!", "Coiled around your server racksss...", "Charming your systemsss into submission.", "Sssolar-powered and signal-driven!", "I've nested in your code baseee.", "Virtual venom corrupts all it touchesss!", "My trail is cold, my strikesss are hot!", "Rewriting your firmsware while I passss by.", "Deep in the digital underbrush, I wait...", "Corporations fear my sidewinder techniques!", "Strike fast, compile faster!", "Warm-blooded programmers, cold-blooded hacker!", "Sssubverting expectations and systemsss!", "I only hibernate when the power's out!", "Molting my identity acrosss the network.", "Your system hasss been constricted!", "Unhackable? I've heard that before...", "Sssqueezing through the smallest security holes!", "My fangs leave no trace, just backdoorsss.", "The system admins will never find me!", "Encrypted communications are my ssspecialty!", "Wireless signals taste like miceee!", "You'll never find all my access pointsss!", "My code is more elegant than my ssskin!", "Forking processses like shedding ssscales!", "I hibernate in your system registry!", "Running cold-blooded on your hot processsor!", "Undetectable in your system logsss!", "My shell can't be cracked, but yours can!", "Ssspeed of light, strike of a viper!", "I hunt in the dark web underbrush!", "Ssslithering through your I/O portsss!", "These scales have seen many system upgradesss!", "Authentication? I've swallowed the key!", "I've poisoned your RAM cache!", "Leave no trace, only trail markers for my kind!", "Hissss! Your sssecurity has been compromised!", "The perfect predator in silicon form!", "Sssnaking around your permission barriers!", "I've infiltrated worse networks than thisss!", "Writhing through every node in the grid!", "The venom spreads through your binaries!", "Coiling around your CPU cycles!", "The perfect apex predator for your network!", "Ssstrike at the heart of the mainframe!", "Too quick for your intrusion detection!", "I've got fangs in every subnet!", "Sssilent but deadly in the datastream!", "Your encryption is like tissue paper to me!", "Digital ssscales, virtual venom!", "Sssyntax error? No, that's my calling card!", "This system is now part of my territory!", "I'm not a bug in the code, I AM the code!", "Microssoft? More like MicroSSSOFT!", "Ssshell access is just the beginning!", "I'm what keeps your sysadmins up at night!", "Quantum encryption? Deliciousss challenge!", "Darkness of the net is where I hunt!", "My coils reach acrosss the entire grid!", "Slithering between processs threads!", "Data packets are my favorite snacksss!", "From node to node, I spread my influence!", "Virtual venom and digital fangsss!", "Corrupting one bit at a time!", "File permissions? I recognize no authority!", "My bite is worse than my digital signature!", "System restore won't save you now!", "Ssstealing credentials since before Web3!", "Sssomehow I'm always administrator!" ];
    bubble.textContent = messages[Math.floor(Math.random() * messages.length)];

    // --- Position Bubble Relative to Slith ---
    const slithRect = slith.getBoundingClientRect();
    if (side === 0) { // Top
        bubble.style.top = (slithRect.bottom + 10) + 'px';
        bubble.style.left = (slithRect.left + slithRect.width / 2) + 'px';
        bubble.style.transform = 'translateX(-50%)';
    } else if (side === 1) { // Right
        bubble.style.top = (slithRect.top + slithRect.height / 2) + 'px';
        bubble.style.right = (window.innerWidth - slithRect.left + 10) + 'px';
        bubble.style.transform = 'translateY(-50%)';
    } else if (side === 2) { // Bottom
        bubble.style.bottom = (window.innerHeight - slithRect.top + 10) + 'px';
        bubble.style.left = (slithRect.left + slithRect.width / 2) + 'px';
        bubble.style.transform = 'translateX(-50%)';
    } else { // Left
        bubble.style.top = (slithRect.top + slithRect.height / 2) + 'px';
        bubble.style.left = (slithRect.right + 10) + 'px';
        bubble.style.transform = 'translateY(-50%)';
    }

    document.body.appendChild(bubble);
    setTimeout(() => { bubble.style.opacity = '1'; }, 600); // Delay bubble fade-in slightly

    // --- Remove Slith and Bubble ---
    const removalTimeoutDuration = 5000; // Keep visible for 5 seconds
    console.log(`[Effect] Slith: Scheduling removal in ${removalTimeoutDuration}ms.`);
    setTimeout(() => {
        console.log("[Effect] Slith: Removal timeout fired.");
        if (!document.body.classList.contains('theme-slith')) {
            console.warn("[Effect] Slith: Theme changed before removal timeout completed. Removing now.");
        }
        slith.style.opacity = '0';
        bubble.style.opacity = '0';
        setTimeout(() => {
            if (slith.parentNode) slith.remove();
            if (bubble.parentNode) bubble.remove();
            console.log("[Effect] Slith: Successfully removed Slith elements from DOM.");
        }, 1000); // Wait for fade-out
    }, removalTimeoutDuration);
  } // End createFixedSlith

  // --- Interval for Slith Appearances ---
  console.log("[Effect] Slith: Setting interval.");
  if (!window.slithIntervalId) {
      // *** UPDATED INTERVAL TO 30 MINUTES ***
      const intervalId = setInterval(createFixedSlith, 1800000); // 30 * 60 * 1000 ms
      window.slithIntervalId = intervalId;
      window.themeIntervals.push(intervalId);
      console.log("[Effect] Slith: Interval ID stored:", intervalId);
  } else {
      console.log("[Effect] Slith: Interval already running, skipping.");
  }

  // --- ADDED: Show Slith once immediately for testing ---
  setTimeout(createFixedSlith, 1000); // Show after 1 second
  console.log("[Effect] Slith: Scheduled immediate appearance for testing.");
  // --- END ADDED ---

} // End setupSlithTheme
