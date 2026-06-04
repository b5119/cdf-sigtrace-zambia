// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CDF Pulse Multi-Party Confirmation
/// @notice Records field-evidence submissions and requires N distinct
///         institutional confirmations before a project is marked complete.
///         A single party cannot complete a submission alone — this is the
///         core anti-fraud guarantee of the CDF Pulse delivery layer.
contract CDFConfirmation {
    struct Submission {
        string ipfsCid;              // content-addressed evidence photo (INC-011)
        uint8 requiredConfirmations; // N distinct confirmers needed
        uint8 confirmationCount;     // confirmations received so far
        bool exists;
        bool complete;               // true once confirmationCount >= required
        address monitor;             // who recorded the submission
        uint256 recordedAt;
    }

    /// @dev submissionId is keccak256 of the off-chain submission UUID
    mapping(bytes32 => Submission) public submissions;
    /// @dev tracks which addresses have confirmed each submission (distinctness)
    mapping(bytes32 => mapping(address => bool)) public hasConfirmed;
    /// @dev whitelist of institutional confirmers (council/ward officers, OAG)
    mapping(address => bool) public authorizedConfirmers;

    address public owner;

    event SubmissionRecorded(bytes32 indexed submissionId, string ipfsCid, uint8 required, address indexed monitor);
    event Confirmed(bytes32 indexed submissionId, address indexed confirmer, uint8 count);
    event SubmissionCompleted(bytes32 indexed submissionId, uint8 confirmations);
    event ConfirmerAdded(address indexed confirmer);
    event ConfirmerRemoved(address indexed confirmer);

    modifier onlyOwner() {
        require(msg.sender == owner, "CDF: not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // ── Confirmer governance ──────────────────────────────────────────────────

    function addConfirmer(address confirmer) external onlyOwner {
        require(confirmer != address(0), "CDF: zero address");
        authorizedConfirmers[confirmer] = true;
        emit ConfirmerAdded(confirmer);
    }

    function removeConfirmer(address confirmer) external onlyOwner {
        authorizedConfirmers[confirmer] = false;
        emit ConfirmerRemoved(confirmer);
    }

    // ── Submission lifecycle ──────────────────────────────────────────────────

    /// @notice Record a new field-evidence submission requiring `required` confirmations.
    function recordSubmission(
        bytes32 submissionId,
        string calldata ipfsCid,
        uint8 required
    ) external {
        require(!submissions[submissionId].exists, "CDF: already recorded");
        require(required > 0, "CDF: required must be > 0");

        submissions[submissionId] = Submission({
            ipfsCid: ipfsCid,
            requiredConfirmations: required,
            confirmationCount: 0,
            exists: true,
            complete: false,
            monitor: msg.sender,
            recordedAt: block.timestamp
        });

        emit SubmissionRecorded(submissionId, ipfsCid, required, msg.sender);
    }

    /// @notice Confirm a submission. Must be a distinct authorized confirmer,
    ///         not the original monitor, and cannot confirm twice.
    function confirm(bytes32 submissionId) external {
        Submission storage s = submissions[submissionId];
        require(s.exists, "CDF: unknown submission");
        require(!s.complete, "CDF: already complete");
        require(authorizedConfirmers[msg.sender], "CDF: not authorized confirmer");
        require(msg.sender != s.monitor, "CDF: monitor cannot self-confirm");
        require(!hasConfirmed[submissionId][msg.sender], "CDF: duplicate confirmation");

        hasConfirmed[submissionId][msg.sender] = true;
        s.confirmationCount += 1;
        emit Confirmed(submissionId, msg.sender, s.confirmationCount);

        if (s.confirmationCount >= s.requiredConfirmations) {
            s.complete = true;
            emit SubmissionCompleted(submissionId, s.confirmationCount);
        }
    }

    // ── Views ─────────────────────────────────────────────────────────────────

    function isComplete(bytes32 submissionId) external view returns (bool) {
        return submissions[submissionId].complete;
    }

    function getConfirmationCount(bytes32 submissionId) external view returns (uint8) {
        return submissions[submissionId].confirmationCount;
    }

    function getSubmission(bytes32 submissionId)
        external
        view
        returns (string memory ipfsCid, uint8 required, uint8 count, bool complete, address monitor)
    {
        Submission storage s = submissions[submissionId];
        require(s.exists, "CDF: unknown submission");
        return (s.ipfsCid, s.requiredConfirmations, s.confirmationCount, s.complete, s.monitor);
    }
}
