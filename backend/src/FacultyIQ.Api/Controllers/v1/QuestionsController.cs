using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using FacultyIQ.Application.Abstractions.Data;

namespace FacultyIQ.Api.Controllers.v1;

[ApiController]
[Route("api/v1/[controller]")]
public class QuestionsController : ControllerBase
{
    private readonly IApplicationDbContext _context;

    public QuestionsController(IApplicationDbContext context)
    {
        _context = context;
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetQuestion(Guid id, CancellationToken cancellationToken)
    {
        // Mocking the response for the frontend scaffold
        var question = new 
        {
            Id = id,
            Title = "Two Sum",
            Description = "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            Constraints = "- 2 <= nums.length <= 10^4\n- -10^9 <= nums[i] <= 10^9\n- -10^9 <= target <= 10^9\n- Only one valid answer exists.",
            StarterCodeJson = "{ \"python\": \"class Solution:\\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\\n        pass\", \"cpp\": \"class Solution {\\npublic:\\n    vector<int> twoSum(vector<int>& nums, int target) {\\n        \\n    }\\n};\" }"
        };

        return Ok(question);
    }
}
