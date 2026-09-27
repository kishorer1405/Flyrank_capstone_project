/* =========================================================
   FlyRank Capture — Owner Dashboard
   ========================================================= */

/* ---------------------------------------------------------
   Configuration
--------------------------------------------------------- */

const API_BASE_URL = "http://localhost:8000";

const token = localStorage.getItem("flyrank_token");


/* ---------------------------------------------------------
   Authentication Guard
--------------------------------------------------------- */

if (!token) {
    window.location.href = "login.html";
}


/* ---------------------------------------------------------
   DOM Helpers
--------------------------------------------------------- */

const $ = (selector) => document.querySelector(selector);

const totalElement = $("#total");
const widgetsElement = $("#widgets");
const timelineElement = $("#timeline");
const tableElement = $("#table");
const geoElement = $("#geo");
const logoutButton = $("#logout");


/* ---------------------------------------------------------
   Utility Functions
--------------------------------------------------------- */

/**
 * Escape HTML before inserting API data into innerHTML.
 * This prevents user-submitted lead data from becoming HTML.
 */
function escapeHTML(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/**
 * Format date/time in the user's local timezone.
 */
function formatDate(dateValue) {

    if (!dateValue) {
        return "—";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short"
    });
}


/**
 * Safely get the main lead identifier.
 */
function getLeadName(data) {

    if (!data || typeof data !== "object") {
        return "Lead";
    }

    return (
        data.email ||
        data.name ||
        data.full_name ||
        data.phone ||
        "Lead"
    );
}


/* ---------------------------------------------------------
   API Client
--------------------------------------------------------- */

async function api(path, options = {}) {

    const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
            ...options,

            headers: {
                ...(options.headers || {}),
                Authorization: `Bearer ${token}`,
                Accept: "application/json"
            }
        }
    );


    /* -----------------------------------------------------
       Authentication expired
    ----------------------------------------------------- */

    if (response.status === 401) {

        localStorage.removeItem("flyrank_token");

        window.location.href = "login.html";

        return null;
    }


    /* -----------------------------------------------------
       Parse response
    ----------------------------------------------------- */

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }


    /* -----------------------------------------------------
       Handle API errors
    ----------------------------------------------------- */

    if (!response.ok) {

        const errorMessage =
            data?.detail ||
            data?.message ||
            `Request failed (${response.status})`;

        throw new Error(errorMessage);
    }


    return data;
}


/* ---------------------------------------------------------
   Dashboard Loading State
--------------------------------------------------------- */

function showLoadingState() {

    if (totalElement) {
        totalElement.textContent = "—";
    }

    if (widgetsElement) {
        widgetsElement.textContent = "—";
    }

    if (timelineElement) {
        timelineElement.innerHTML = `
            <div class="dashboard-loading">
                Loading analytics...
            </div>
        `;
    }

    if (tableElement) {
        tableElement.innerHTML = `
            <div class="dashboard-loading">
                Loading submissions...
            </div>
        `;
    }

    if (geoElement) {
        geoElement.innerHTML = `
            <div class="dashboard-loading">
                Loading geographic data...
            </div>
        `;
    }
}


/* ---------------------------------------------------------
   Statistics
--------------------------------------------------------- */

function renderStats(stats) {

    if (!stats) {
        return;
    }

    if (totalElement) {

        totalElement.textContent =
            Number(stats.total_submissions || 0).toLocaleString();
    }


    if (widgetsElement) {

        widgetsElement.textContent =
            Number(stats.total_widgets || 0).toLocaleString();
    }
}


/* ---------------------------------------------------------
   Submission Timeline
--------------------------------------------------------- */

function renderTimeline(data) {

    if (!timelineElement) {
        return;
    }


    const timeline =
        Array.isArray(data?.submissions_over_time)
            ? data.submissions_over_time
            : [];


    /* Empty state */

    if (!timeline.length) {

        timelineElement.innerHTML = `
            <div class="dashboard-empty">
                <div class="empty-icon">📊</div>
                <strong>No submissions yet</strong>
                <span>Your submission activity will appear here.</span>
            </div>
        `;

        return;
    }


    const counts = timeline.map(
        item => Number(item.count || 0)
    );


    const maxCount =
        Math.max(1, ...counts);


    timelineElement.innerHTML =
        timeline.map((item) => {

            const count =
                Number(item.count || 0);

            const height =
                30 + (count / maxCount) * 110;


            const label =
                item.date ||
                item.day ||
                item.label ||
                "";


            return `
                <div
                    class="bar-wrapper"
                    title="${escapeHTML(label)}: ${count} submission(s)"
                >

                    <div
                        class="bar"
                        style="height: ${height}px"
                    >
                        <small>
                            ${count}
                        </small>
                    </div>

                    <span class="bar-label">
                        ${escapeHTML(label)}
                    </span>

                </div>
            `;

        }).join("");
}


/* ---------------------------------------------------------
   Submissions Table
--------------------------------------------------------- */

function renderSubmissions(data) {

    if (!tableElement) {
        return;
    }


    const submissions =
        Array.isArray(data?.items)
            ? data.items
            : [];


    /* Empty state */

    if (!submissions.length) {

        tableElement.innerHTML = `
            <div class="dashboard-empty">
                <div class="empty-icon">📥</div>
                <strong>No submissions yet</strong>
                <span>
                    Leads captured through your widgets
                    will appear here.
                </span>
            </div>
        `;

        return;
    }


    tableElement.innerHTML =
        submissions.map((submission) => {

            const leadData =
                submission.data || {};


            const lead =
                getLeadName(leadData);


            const city =
                submission.city ||
                "—";


            const country =
                submission.country ||
                "—";


            return `
                <div class="row">

                    <span>
                        ${escapeHTML(
                            formatDate(submission.created_at)
                        )}
                    </span>

                    <span
                        class="lead-name"
                        title="${escapeHTML(lead)}"
                    >
                        ${escapeHTML(lead)}
                    </span>

                    <span>
                        ${escapeHTML(city)}
                    </span>

                    <span>
                        ${escapeHTML(country)}
                    </span>

                </div>
            `;

        }).join("");
}


/* ---------------------------------------------------------
   Geographic Breakdown
--------------------------------------------------------- */

function renderGeoBreakdown(data) {

    if (!geoElement) {
        return;
    }


    const geo =
        Array.isArray(data?.geo_breakdown)
            ? data.geo_breakdown
            : [];


    /* Empty state */

    if (!geo.length) {

        geoElement.innerHTML = `
            <div class="dashboard-empty">
                <div class="empty-icon">🌍</div>
                <strong>No geographic data</strong>
                <span>
                    Location information will appear
                    after submissions are received.
                </span>
            </div>
        `;

        return;
    }


    const total =
        geo.reduce(
            (sum, item) =>
                sum + Number(item.count || 0),
            0
        );


    geoElement.innerHTML =
        geo.map((item) => {

            const country =
                item.country || "Unknown";


            const count =
                Number(item.count || 0);


            const percentage =
                total > 0
                    ? Math.round((count / total) * 100)
                    : 0;


            return `
                <div class="geo-item">

                    <div class="geo-header">

                        <strong>
                            ${escapeHTML(country)}
                        </strong>

                        <span>
                            ${count}
                            submission${count === 1 ? "" : "s"}
                        </span>

                    </div>

                    <div class="geo-progress">

                        <div
                            class="geo-progress-bar"
                            style="width: ${percentage}%"
                        ></div>

                    </div>

                    <small>
                        ${percentage}% of submissions
                    </small>

                </div>
            `;

        }).join("");
}


/* ---------------------------------------------------------
   Global Error State
--------------------------------------------------------- */

function showDashboardError(error) {

    console.error(
        "Dashboard error:",
        error
    );


    if (tableElement) {

        tableElement.innerHTML = `
            <div class="dashboard-error">

                <div class="error-icon">
                    ⚠
                </div>

                <strong>
                    Unable to load dashboard
                </strong>

                <span>
                    ${escapeHTML(
                        error?.message ||
                        "Please make sure the API server is running."
                    )}
                </span>

                <button
                    type="button"
                    onclick="window.location.reload()"
                >
                    Try again
                </button>

            </div>
        `;
    }
}


/* ---------------------------------------------------------
   Load Dashboard
--------------------------------------------------------- */

async function loadDashboard() {

    showLoadingState();


    try {

        /* ---------------------------------------------
           Load statistics
        --------------------------------------------- */

        const stats =
            await api(
                "/api/v1/dashboard/stats"
            );


        if (!stats) {
            return;
        }


        renderStats(stats);

        renderTimeline(stats);

        renderGeoBreakdown(stats);


        /* ---------------------------------------------
           Load submissions
        --------------------------------------------- */

        const submissions =
            await api(
                "/api/v1/dashboard/submissions"
            );


        if (!submissions) {
            return;
        }


        renderSubmissions(submissions);


    } catch (error) {

        showDashboardError(error);
    }
}


/* ---------------------------------------------------------
   Logout
--------------------------------------------------------- */

function logout() {

    localStorage.removeItem(
        "flyrank_token"
    );

    window.location.href =
        "login.html";
}


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        logout
    );
}


/* ---------------------------------------------------------
   Start Dashboard
--------------------------------------------------------- */

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);