(function () {
  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  var header = document.getElementById("siteHeader");
  function onScroll() {
    if (header) header.classList.toggle("stuck", window.scrollY > 6);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  var menuBtn = document.getElementById("menuBtn");
  var navLinks = document.getElementById("navLinks");
  function closeMenu() {
    if (!navLinks || !menuBtn) return;
    navLinks.classList.remove("open");
    menuBtn.setAttribute("aria-expanded", "false");
  }
  if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function () {
      var open = navLinks.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    navLinks.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu();
    });
  }

  var toast = document.getElementById("toast");
  var toastTimer;
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("show"); }, 1900);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy") ? resolve() : reject();
      } catch (err) {
        reject(err);
      }
      document.body.removeChild(ta);
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".copy");
    if (!btn) return;
    e.preventDefault();
    var text = btn.getAttribute("data-copy") || "";
    copyText(text).then(function () {
      var old = btn.textContent;
      btn.classList.add("ok");
      btn.textContent = "Готово";
      showToast(text.length > 40 ? "Адрес скопирован" : "Скопировано");
      setTimeout(function () {
        btn.classList.remove("ok");
        btn.textContent = old;
      }, 1600);
    }).catch(function () {
      showToast("Не удалось скопировать");
    });
  });

  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  var shots = document.getElementById("shots");
  var shotsPrev = document.getElementById("shotsPrev");
  var shotsNext = document.getElementById("shotsNext");
  function shotStep() {
    var first = shots ? shots.querySelector(".shot") : null;
    return first ? first.getBoundingClientRect().width + 12 : 420;
  }
  function updateShots() {
    if (!shots) return;
    var max = shots.scrollWidth - shots.clientWidth - 2;
    if (shotsPrev) shotsPrev.disabled = shots.scrollLeft <= 2;
    if (shotsNext) shotsNext.disabled = shots.scrollLeft >= max;
  }
  if (shots) {
    if (shotsPrev) shotsPrev.addEventListener("click", function () { shots.scrollBy({ left: -shotStep(), behavior: "smooth" }); });
    if (shotsNext) shotsNext.addEventListener("click", function () { shots.scrollBy({ left: shotStep(), behavior: "smooth" }); });
    shots.addEventListener("scroll", updateShots, { passive: true });
    window.addEventListener("resize", updateShots);
    updateShots();
  }

  var lightbox = document.getElementById("lightbox");
  var lbImg = document.getElementById("lbImg");
  var lbCap = document.getElementById("lbCap");
  var lbIndex = document.getElementById("lbIndex");
  var lbClose = document.getElementById("lbClose");
  var lbPrev = document.getElementById("lbPrev");
  var lbNext = document.getElementById("lbNext");
  var shotButtons = Array.prototype.slice.call(document.querySelectorAll(".shot button"));
  var lbPos = 0;
  var lastFocus = null;

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function renderLb() {
    var btn = shotButtons[lbPos];
    if (!btn) return;
    var img = btn.querySelector("img");
    var full = btn.getAttribute("data-full") || (img ? img.src : "");
    lbImg.src = full;
    lbImg.alt = img ? img.alt : "";
    lbCap.textContent = btn.getAttribute("data-cap") || "";
    lbIndex.textContent = pad(lbPos + 1);
  }

  function openLb(index) {
    if (!lightbox || !shotButtons.length) return;
    lastFocus = document.activeElement;
    lbPos = index;
    renderLb();
    lightbox.classList.add("open");
    document.body.style.overflow = "hidden";
    lbClose.focus();
  }

  function closeLb() {
    if (!lightbox) return;
    lightbox.classList.remove("open");
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  shotButtons.forEach(function (btn, index) {
    btn.addEventListener("click", function () { openLb(index); });
  });
  if (lbClose) lbClose.addEventListener("click", closeLb);
  if (lbPrev) lbPrev.addEventListener("click", function () {
    lbPos = (lbPos - 1 + shotButtons.length) % shotButtons.length;
    renderLb();
  });
  if (lbNext) lbNext.addEventListener("click", function () {
    lbPos = (lbPos + 1) % shotButtons.length;
    renderLb();
  });
  if (lightbox) {
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) closeLb();
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeMenu();
      if (lightbox && lightbox.classList.contains("open")) closeLb();
    }
    if (lightbox && lightbox.classList.contains("open")) {
      if (e.key === "ArrowLeft" && lbPrev) lbPrev.click();
      if (e.key === "ArrowRight" && lbNext) lbNext.click();
    }
  });

  var snippets = [
    { label: "ПРИВЕТ", text: "Привет! Как дела?" },
    { label: "СПС", text: "Спасибо!" },
    { label: "1 МИН", text: "Секунду, я сейчас." },
    { label: "ПОЗЖЕ", text: "Давай позже." },
    { label: "СОЗВОН", text: "Созвонимся?" },
    { label: "ОК", text: "Ок, договорились." }
  ];
  var sectors = Array.prototype.slice.call(document.querySelectorAll(".sector"));
  var wheelLabel = document.getElementById("wheelLabel");
  var wheelText = document.getElementById("wheelText");
  var demoInput = document.getElementById("demoInput");
  var demoForm = document.getElementById("demoForm");
  var chatLog = document.getElementById("chatLog");
  var chatEmpty = document.getElementById("chatEmpty");
  var demoStatus = document.getElementById("demoStatus");
  var demoReset = document.getElementById("demoReset");
  var emptyMarkup = chatLog ? chatLog.innerHTML : "";

  function selectSector(index) {
    sectors.forEach(function (s, i) { s.classList.toggle("is-active", i === index); });
    if (wheelLabel) wheelLabel.textContent = snippets[index].label;
    if (wheelText) wheelText.textContent = snippets[index].text;
  }

  function insertSnippet(index) {
    if (!demoInput) return;
    selectSector(index);
    demoInput.value = snippets[index].text;
    demoInput.focus();
    if (demoStatus) demoStatus.textContent = "Enter — отправить";
    showToast("Вставлено: " + snippets[index].label);
  }

  sectors.forEach(function (sector, index) {
    sector.addEventListener("mouseenter", function () { selectSector(index); });
    sector.addEventListener("focus", function () { selectSector(index); });
    sector.addEventListener("click", function () { insertSnippet(index); });
    sector.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        insertSnippet(index);
      }
    });
  });

  function autoGrow() {
    if (!demoInput) return;
    demoInput.style.height = "auto";
    demoInput.style.height = Math.min(demoInput.scrollHeight, 110) + "px";
  }
  if (demoInput) demoInput.addEventListener("input", autoGrow);

  function sendDemo() {
    if (!demoInput || !chatLog) return;
    var text = demoInput.value.trim();
    if (!text) {
      if (demoStatus) demoStatus.textContent = "Сначала выбери сектор";
      showToast("Выбери сектор на колесе");
      return;
    }
    if (chatEmpty) chatEmpty.remove();
    var bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    var time = document.createElement("span");
    time.className = "time";
    time.textContent = "сейчас";
    bubble.appendChild(time);
    chatLog.appendChild(bubble);
    chatLog.scrollTop = chatLog.scrollHeight;
    demoInput.value = "";
    demoInput.style.height = "38px";
    if (demoStatus) demoStatus.textContent = "Отправлено";
    showToast("Сообщение отправлено");
  }

  if (demoForm) {
    demoForm.addEventListener("submit", function (e) {
      e.preventDefault();
      sendDemo();
    });
  }

  if (demoInput) {
    demoInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendDemo();
      }
    });
  }

  if (demoReset) {
    demoReset.addEventListener("click", function () {
      if (!chatLog) return;
      chatLog.innerHTML = emptyMarkup;
      chatEmpty = document.getElementById("chatEmpty");
      sectors.forEach(function (s) { s.classList.remove("is-active"); });
      if (wheelLabel) wheelLabel.textContent = "НАВЕДИ";
      if (wheelText) wheelText.textContent = "и выбери сектор";
      if (demoInput) {
        demoInput.value = "";
        demoInput.style.height = "38px";
      }
      if (demoStatus) demoStatus.textContent = "Enter — отправить";
    });
  }

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
