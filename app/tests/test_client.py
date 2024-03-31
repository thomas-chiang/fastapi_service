from app.application import app
import time

def test_report_match_times(client, bit_repository, pi_notation_score_repository):
    request_body = {
        "source": "sample_channel",
        "url": "url_for_random_bytes",
        "threshold": 100
    }
    with app.container.bit_repository.override(bit_repository), app.container.pi_notation_score_repository.override(pi_notation_score_repository):
        for i in range(11):
            response = client.post("/report", json=request_body)
            time.sleep(1)
    assert response.status_code == 200
    data = response.json()
    assert data.get('channel') == "sample_channel"
    assert isinstance(data.get('time'), int)
    assert isinstance(data.get('match_times'), list)
    assert all(isinstance(item, int) for item in data.get('match_times'))