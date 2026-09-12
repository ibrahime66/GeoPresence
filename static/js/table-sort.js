/*
 * Tri des colonnes au clic — s'applique automatiquement à tous les tableaux
 * `.gp-table` du site (listes employés, agences, congés, absences...), sans
 * modifier chaque template un par un. Purement côté client : trie les lignes
 * déjà affichées à l'écran (pas de rechargement serveur), ce qui suffit pour
 * les tableaux paginés côté serveur — trier une page à la fois reste très
 * utile et évite d'ajouter un tri serveur à chaque vue.
 *
 * Opt-out : mettre `data-no-sort` sur un `<th>` pour le rendre non triable
 * (ex. colonne d'actions). Une cellule peut aussi fournir une valeur de tri
 * explicite via `<td data-sort-value="...">` si le texte affiché n'est pas
 * directement comparable (ex. badge de statut avec icône).
 */
(() => {
  const collator = new Intl.Collator("fr", { numeric: true, sensitivity: "base" });

  function isEmptyValue(text) {
    const t = (text || "").trim();
    return t === "" || t === "—" || t === "-";
  }

  function parseSortValue(text) {
    const t = text.trim();
    // Dates : dd/mm/yyyy ou dd/mm (année en cours par défaut), avec heure
    // optionnelle "HH:mm" — couvre les formats utilisés par les templates
    // (ex. "12/09/2026", "12/09/2026 14:30", "12/09").
    const dateMatch = t.match(/^(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?(?:[ T](\d{1,2}):(\d{2}))?$/);
    if (dateMatch) {
      const [, day, month, year, hour, minute] = dateMatch;
      const fullYear = year ? (year.length === 2 ? 2000 + Number(year) : Number(year)) : new Date().getFullYear();
      const date = new Date(fullYear, Number(month) - 1, Number(day), Number(hour || 0), Number(minute || 0));
      if (!Number.isNaN(date.getTime())) return { type: "number", value: date.getTime() };
    }
    // Nombres : entiers/décimaux, espace ou espace insécable en séparateur de
    // milliers, virgule décimale, % final optionnel (ex. "1 250,5", "87%").
    const numMatch = t.match(/^-?[\d\s ]+([.,]\d+)?\s*%?$/);
    if (numMatch) {
      const cleaned = t.replace(/[\s %]/g, "").replace(",", ".");
      const n = parseFloat(cleaned);
      if (!Number.isNaN(n)) return { type: "number", value: n };
    }
    return { type: "text", value: t.toLocaleLowerCase("fr-FR") };
  }

  function compareCells(a, b) {
    const pa = parseSortValue(a);
    const pb = parseSortValue(b);
    if (pa.type === "number" && pb.type === "number") return pa.value - pb.value;
    return collator.compare(pa.value, pb.value);
  }

  function cellSortText(row, colIndex) {
    const cell = row.cells[colIndex];
    if (!cell) return "";
    if (cell.dataset && cell.dataset.sortValue !== undefined) return cell.dataset.sortValue;
    return cell.textContent || "";
  }

  function initTable(table) {
    // Un seul `<tr>` d'en-tête attendu : un thead multi-lignes (colonnes
    // groupées) n'est utilisé nulle part actuellement, et y appliquer un tri
    // par index de colonne serait faux.
    if (!table.tHead || table.tHead.rows.length !== 1) return;
    const tbody = table.tBodies[0];
    if (!tbody) return;
    const ths = Array.from(table.tHead.rows[0].cells);

    ths.forEach((th, index) => {
      const label = th.textContent.trim();
      // Colonnes ignorées : en-tête vide (colonne d'actions), en-tête avec un
      // contrôle interactif (case à cocher globale...), ou opt-out explicite.
      if (!label || th.hasAttribute("data-no-sort") || th.querySelector("input, select, button, a")) return;

      th.classList.add("gp-th-sortable");
      th.setAttribute("role", "button");
      th.setAttribute("tabindex", "0");
      th.setAttribute("aria-sort", "none");
      const icon = document.createElement("span");
      icon.className = "gp-th-sort-icon";
      icon.setAttribute("aria-hidden", "true");
      th.appendChild(icon);

      const applySort = () => {
        const direction = th.dataset.sortDir === "asc" ? "desc" : "asc";
        ths.forEach((other) => {
          delete other.dataset.sortDir;
          other.setAttribute("aria-sort", "none");
          other.classList.remove("is-sorted-asc", "is-sorted-desc");
        });
        th.dataset.sortDir = direction;
        th.setAttribute("aria-sort", direction === "asc" ? "ascending" : "descending");
        th.classList.add(direction === "asc" ? "is-sorted-asc" : "is-sorted-desc");

        // Une ligne d'état vide (`<td colspan>`) n'a pas autant de cellules
        // que l'en-tête : on l'exclut du tri au lieu de planter dessus.
        const rows = Array.from(tbody.rows).filter((row) => row.cells.length === ths.length);
        if (rows.length < 2) return;
        const sign = direction === "asc" ? 1 : -1;

        rows.sort((rowA, rowB) => {
          const valueA = cellSortText(rowA, index);
          const valueB = cellSortText(rowB, index);
          const emptyA = isEmptyValue(valueA);
          const emptyB = isEmptyValue(valueB);
          // Les valeurs manquantes restent toujours en fin de liste, dans les
          // deux sens de tri — sinon trier en décroissant les fait remonter
          // en premier, ce qui surprend plus qu'autre chose.
          if (emptyA && emptyB) return 0;
          if (emptyA) return 1;
          if (emptyB) return -1;
          return compareCells(valueA, valueB) * sign;
        });

        const fragment = document.createDocumentFragment();
        rows.forEach((row) => fragment.appendChild(row));
        tbody.appendChild(fragment);
      };

      th.addEventListener("click", applySort);
      th.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          applySort();
        }
      });
    });
  }

  document.querySelectorAll("table.gp-table").forEach(initTable);
})();
