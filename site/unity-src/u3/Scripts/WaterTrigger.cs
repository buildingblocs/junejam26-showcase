//to detect player
using UnityEngine;

public class WaterTrigger : MonoBehaviour
{
    private GameRules gameRules;

    void Start()
    {
        gameRules =
            FindFirstObjectByType<GameRules>();
    }

    void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            gameRules.PlayerTouchedWater();
        }
    }
}