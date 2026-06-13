(function () {
  const STORAGE_KEY = "laser-v2-concept-language";
  const FALLBACK = "en";

  function browserDefault() {
    const language = (navigator.language || navigator.userLanguage || "").toLowerCase();
    return language.startsWith("de") ? "de" : "en";
  }

  function normalize(language) {
    return language === "de" || language === "en" ? language : FALLBACK;
  }

  function getLanguage() {
    return normalize(localStorage.getItem(STORAGE_KEY) || browserDefault());
  }

  function setLanguage(language) {
    const normalized = normalize(language);
    localStorage.setItem(STORAGE_KEY, normalized);
    document.documentElement.lang = normalized;
    return normalized;
  }

  function valueFor(translations, language, key) {
    return translations?.[language]?.[key] ?? translations?.[FALLBACK]?.[key] ?? "";
  }

  function applyTranslations(translations, language, root = document) {
    document.documentElement.lang = language;
    root.querySelectorAll("[data-i18n]").forEach((node) => {
      const value = valueFor(translations, language, node.dataset.i18n);
      if (value) node.innerHTML = value;
    });
    root.querySelectorAll("[data-i18n-text]").forEach((node) => {
      const value = valueFor(translations, language, node.dataset.i18nText);
      if (value) node.textContent = value;
    });
    root.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      const value = valueFor(translations, language, node.dataset.i18nPlaceholder);
      if (value) node.setAttribute("placeholder", value);
    });
    root.querySelectorAll("[data-i18n-label]").forEach((node) => {
      const value = valueFor(translations, language, node.dataset.i18nLabel);
      if (value) node.setAttribute("aria-label", value);
    });
    root.querySelectorAll("[data-i18n-value]").forEach((node) => {
      const value = valueFor(translations, language, node.dataset.i18nValue);
      if (value && "value" in node) node.value = value;
    });
    root.querySelectorAll("[data-language-switch]").forEach((node) => {
      node.querySelectorAll("[data-lang]").forEach((button) => {
        const active = button.dataset.lang === language;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      });
    });
  }

  function initLanguage(translations, onChange) {
    const language = setLanguage(getLanguage());
    applyTranslations(translations, language);

    document.querySelectorAll("[data-language-switch] [data-lang]").forEach((button) => {
      button.addEventListener("click", () => {
        const nextLanguage = setLanguage(button.dataset.lang);
        applyTranslations(translations, nextLanguage);
        if (typeof onChange === "function") onChange(nextLanguage);
      });
    });

    if (typeof onChange === "function") onChange(language);
    return language;
  }

  window.V2I18n = {
    applyTranslations,
    getLanguage,
    initLanguage,
    normalize,
    setLanguage,
    t(translations, key, language = getLanguage()) {
      return valueFor(translations, language, key);
    }
  };
})();
