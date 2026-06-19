using UnityEngine;

public class DeathTrigger : MonoBehaviour
{
    private GameRules gameRules;

    void Start()
    {
        gameRules =
            FindFirstObjectByType<GameRules>();
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            gameRules.PlayerTouchedWater();
        }
    }
}