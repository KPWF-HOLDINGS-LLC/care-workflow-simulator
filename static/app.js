const cases = document.querySelector("#cases");
const message = document.querySelector("#message");

async function send(path, payload) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Demo action failed");
  render(data.cases);
}

function button(label, action) {
  const element = document.createElement("button");
  element.type = "button";
  element.textContent = label;
  element.addEventListener("click", async () => {
    try { await action(); message.textContent = `${label} completed in the demo`; }
    catch (error) { message.textContent = error.message; }
  });
  return element;
}

function render(state) {
  cases.replaceChildren();
  for (const [caseId, item] of Object.entries(state)) {
    const card = document.createElement("section");
    const heading = document.createElement("h2"); heading.textContent = item.label;
    const status = document.createElement("p"); status.textContent = `Status: ${item.status.replaceAll("_", " ")}`;
    card.append(heading, status);
    if (item.last_reply) {
      const reply = document.createElement("p"); reply.textContent = `Scripted reply: ${item.last_reply}`; card.append(reply);
    }
    if (item.alert) {
      const alert = document.createElement("p"); alert.textContent = `Review alert: ${item.alert}`; card.append(alert);
    }
    card.append(button("Send mock check-in", () => send("/api/check-in", { case_id: caseId })));
    if (item.status === "awaiting_reply") {
      for (const [key, label] of [["okay", "Doing okay"], ["help", "Request follow-up"], ["urgent", "Request urgent help"]]) {
        card.append(button(label, () => send("/api/reply", { case_id: caseId, reply_key: key })));
      }
    }
    if (item.alert === "open") card.append(button("Acknowledge alert", () => send("/api/acknowledge", { case_id: caseId })));
    cases.append(card);
  }
}

document.querySelector("#reset").addEventListener("click", () => send("/api/reset", {}));
fetch("/api/state").then(response => response.json()).then(data => render(data.cases)).catch(() => { message.textContent = "Unable to load demo state"; });
