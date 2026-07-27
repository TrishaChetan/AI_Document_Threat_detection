function RecommendationCard({ recommendation }) {
    return (
        <div className="bg-green-950 border border-green-600 rounded-xl p-5">

            <h2 className="text-lg font-bold text-green-300">
                {recommendation.title}
            </h2>

            <ul className="list-disc pl-6 mt-4 space-y-2">
                {recommendation.recommendation?.remediation_steps?.map(
                    (step, index) => (
                        <li key={index}>
                            {step}
                        </li>
                    )
                )}
            </ul>

        </div>
    );
}

export default RecommendationCard;