class StargazingCard extends HTMLElement {
  setConfig(config) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content"></div>
        </ha-card>
      `;
      this.content = this.querySelector('div');
    }
    this.config = config;
  }

  set hass(hass) {
    const entityId = this.config.entity || 'sensor.stargazing_conditions_quality';
    const qualityEntity = hass.states[entityId];

    if (!qualityEntity) {
      this.content.innerHTML = `
        <div style="padding: 16px;">
          <p>Entity not found: ${entityId}</p>
          <p>Please configure the Stargazing integration first.</p>
        </div>
      `;
      return;
    }

    // Get all stargazing entities
    const ratingEntity = hass.states['sensor.stargazing_conditions_rating'];
    const startEntity = hass.states['sensor.stargazing_conditions_optimal_start'];
    const endEntity = hass.states['sensor.stargazing_conditions_optimal_end'];
    const event1 = hass.states['sensor.stargazing_conditions_next_event'];
    const event2 = hass.states['sensor.stargazing_conditions_next_event_2'];
    const event3 = hass.states['sensor.stargazing_conditions_next_event_3'];

    const score = parseInt(qualityEntity.state) || 0;
    const rating = ratingEntity ? ratingEntity.state : 'Unknown';
    const emoji = ratingEntity && ratingEntity.attributes.emoji ? ratingEntity.attributes.emoji : '⭐';

    // Determine color based on score
    let color = '#9e9e9e';
    if (score >= 90) color = '#4caf50';
    else if (score >= 80) color = '#8bc34a';
    else if (score >= 60) color = '#ffc107';
    else color = '#f44336';

    this.content.innerHTML = `
      <style>
        .stargazing-card {
          padding: 16px;
        }
        .score-section {
          text-align: center;
          margin-bottom: 20px;
        }
        .score-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          margin: 0 auto 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36px;
          font-weight: bold;
          color: white;
          background: ${color};
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .rating-text {
          font-size: 24px;
          font-weight: 500;
          margin-bottom: 4px;
        }
        .rating-emoji {
          font-size: 32px;
        }
        .viewing-window {
          background: var(--card-background-color);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 16px;
          border: 1px solid var(--divider-color);
        }
        .viewing-window-title {
          font-size: 14px;
          color: var(--secondary-text-color);
          margin-bottom: 8px;
        }
        .viewing-times {
          display: flex;
          justify-content: space-around;
        }
        .time-block {
          text-align: center;
        }
        .time-label {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        .time-value {
          font-size: 18px;
          font-weight: 500;
        }
        .events-section {
          margin-top: 16px;
        }
        .events-title {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 12px;
          color: var(--primary-text-color);
        }
        .event-item {
          background: var(--card-background-color);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 8px;
          border-left: 4px solid #2196f3;
          border: 1px solid var(--divider-color);
        }
        .event-name {
          font-weight: 500;
          margin-bottom: 4px;
          color: var(--primary-text-color);
        }
        .event-details {
          font-size: 13px;
          color: var(--secondary-text-color);
        }
        .no-events {
          text-align: center;
          padding: 20px;
          color: var(--secondary-text-color);
          font-style: italic;
        }
      </style>

      <div class="stargazing-card">
        <!-- Score Circle -->
        <div class="score-section">
          <div class="score-circle">${score}%</div>
          <div class="rating-text">${rating}</div>
          <div class="rating-emoji">${emoji}</div>
        </div>

        <!-- Viewing Window -->
        ${startEntity && endEntity ? `
        <div class="viewing-window">
          <div class="viewing-window-title">Tonight's Viewing Window</div>
          <div class="viewing-times">
            <div class="time-block">
              <div class="time-label">Start</div>
              <div class="time-value">${startEntity.state}</div>
            </div>
            <div class="time-block">
              <div class="time-label">End</div>
              <div class="time-value">${endEntity.state}</div>
            </div>
          </div>
        </div>
        ` : ''}

        <!-- Events -->
        <div class="events-section">
          <div class="events-title">🌟 Upcoming Astronomy Events</div>
          ${this._renderEvents([event1, event2, event3])}
        </div>
      </div>
    `;
  }

  _renderEvents(events) {
    const validEvents = events.filter(e => e && e.state !== 'No event scheduled');

    if (validEvents.length === 0) {
      return '<div class="no-events">No major events scheduled in the next 30 days</div>';
    }

    return validEvents.map(event => `
      <div class="event-item">
        <div class="event-name">${event.state}</div>
        ${event.attributes.description ? `
          <div class="event-details">${event.attributes.description}</div>
        ` : ''}
      </div>
    `).join('');
  }

  getCardSize() {
    return 5;
  }

  static getConfigElement() {
    return document.createElement("stargazing-card-editor");
  }

  static getStubConfig() {
    return { entity: "sensor.stargazing_conditions_quality" };
  }
}

customElements.define('stargazing-card', StargazingCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'stargazing-card',
  name: 'Stargazing Card',
  description: 'Display stargazing conditions and upcoming astronomy events',
  preview: true,
});
